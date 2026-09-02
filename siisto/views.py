"""
Siisto Fitness App — Views
Complete, production-ready view layer with:
- Real PayPal payment integration
- Real AI recommendations (Gemini)
- Context-aware chatbot with conversation history
- Real chart data from DB
- 90-Day Challenge tracking
- Notification system
- Full profile management
"""
import json
import uuid
import logging
import datetime
import hmac
import hashlib
import base64
import re

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth, TruncDate
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone, translation
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

LANGUAGE_SESSION_KEY = getattr(translation, 'LANGUAGE_SESSION_KEY', '_language')

from .models import (
    Meal, Workout, ChatMessage, ExerciseLibrary,
    WeightLog, Profile, PaymentTransaction, Routine90, Notification
)
from .gemini import ask_gemini, estimate_macros_with_gemini, analyze_meal_photo_with_gemini

logger = logging.getLogger('siisto')

PRO_PRICE_MONTHLY = 9.99
PRO_PRICE_ANNUAL = 89.99
FREE_CHATBOT_DAILY_LIMIT = 5
FREE_FOOD_SCAN_DAILY_LIMIT = 2


# ═══════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════

def get_or_create_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def require_pro(view_func):
    """Decorator that enforces Pro membership."""
    @login_required
    def wrapper(request, *args, **kwargs):
        profile = get_or_create_profile(request.user)
        if not profile.has_active_pro:
            messages.warning(request, "Feejignaanshaha: Astaamahan waxay u baahan tahay Siisto Pro xubinnimada.")
            return redirect('upgrade_pro')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_paypal_access_token():
    """Get a fresh PayPal OAuth2 access token using client credentials."""
    url = f"{settings.PAYPAL_API_BASE}/v1/oauth2/token"
    try:
        resp = requests.post(
            url,
            data={'grant_type': 'client_credentials'},
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get('access_token')
    except Exception as e:
        logger.error(f"PayPal access token error: {e}")
        return None


def get_real_chart_data(user, months=6):
    """Generates real monthly workout count data for the dashboard chart."""
    from datetime import date
    today = date.today()
    result_months = []
    result_values = []
    for i in range(months - 1, -1, -1):
        dt = today.replace(day=1) - datetime.timedelta(days=i * 28)
        month_start = dt.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1)
        count = Workout.objects.filter(
            user=user,
            date__date__gte=month_start,
            date__date__lt=month_end,
        ).count()
        result_months.append(month_start.strftime('%b'))
        result_values.append(count)
    return result_months, result_values


def get_workout_streak(user):
    """Calculate current consecutive workout days streak."""
    today = timezone.now().date()
    streak = 0
    current_date = today
    for _ in range(365):
        has_workout = Workout.objects.filter(
            user=user, date__date=current_date
        ).exists()
        if has_workout:
            streak += 1
            current_date -= datetime.timedelta(days=1)
        else:
            if current_date == today:
                # Check yesterday too (user may not have worked out yet today)
                current_date -= datetime.timedelta(days=1)
                continue
            break
    return streak


def create_notification(user, notification_type, title, message, action_url='', scheduled_for=None):
    """Utility to create a notification for a user."""
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        action_url=action_url,
        scheduled_for=scheduled_for or timezone.now(),
    )


# ═══════════════════════════════════════════════════
#  DASHBOARD / INDEX
# ═══════════════════════════════════════════════════

@login_required
def index(request):
    profile = get_or_create_profile(request.user)

    meals = Meal.objects.filter(user=request.user).order_by('-date')[:6]
    workouts = Workout.objects.filter(user=request.user).order_by('-date')[:6]
    payments = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')[:5]

    today = timezone.now().date()
    today_meals = Meal.objects.filter(user=request.user, date__date=today)
    today_calories = today_meals.aggregate(Sum('calories'))['calories__sum'] or 0
    today_protein = today_meals.aggregate(Sum('protein'))['protein__sum'] or 0

    total_meals_count = Meal.objects.filter(user=request.user).count()
    total_workouts_count = Workout.objects.filter(user=request.user).count()
    workout_streak = get_workout_streak(request.user)

    # Real chart data from DB
    chart_months, chart_values = get_real_chart_data(request.user, months=6)

    # Recent activity feed
    recent_transactions = []
    for p in payments:
        recent_transactions.append({
            'name': p.plan_name,
            'user_name': request.user.username.title(),
            'id_code': f"#{p.transaction_id[:8].upper()}",
            'amount': f"${p.amount:.2f}",
            'status': p.get_status_display(),
            'type': 'pro_sub',
            'date': p.created_at,
            'is_paid': p.status == 'completed',
        })
    for m in meals:
        recent_transactions.append({
            'name': f"Nutrition: {m.name}",
            'user_name': request.user.username.title(),
            'id_code': f"#NUT-{m.id:05d}",
            'amount': f"{m.calories} kcal",
            'status': 'Completed',
            'type': 'meal',
            'date': m.date,
            'is_paid': False,
        })
    for w in workouts:
        recent_transactions.append({
            'name': f"Workout: {w.name}",
            'user_name': request.user.username.title(),
            'id_code': f"#WRK-{w.id:05d}",
            'amount': f"{w.duration} mins",
            'status': 'Completed',
            'type': 'workout',
            'date': w.date,
            'is_paid': False,
        })

    recent_transactions = sorted(recent_transactions, key=lambda x: x['date'], reverse=True)[:8]

    # Unread notifications count
    unread_notifications_count = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()

    # 90-day challenge
    active_challenge = Routine90.objects.filter(user=request.user, is_active=True).first()

    # Check premium expiry and notify
    if profile.has_active_pro and profile.pro_expires_at:
        days_until_expiry = (profile.pro_expires_at - timezone.now()).days
        if days_until_expiry <= 7 and not Notification.objects.filter(
            user=request.user,
            notification_type='premium',
            created_at__date=today,
        ).exists():
            create_notification(
                request.user, 'premium',
                'Premium Expiring Soon',
                f'Your Siisto Pro membership expires in {days_until_expiry} days. Renew now!',
                action_url='/upgrade-pro/',
            )

    context = {
        'profile': profile,
        'meals': meals,
        'workouts': workouts,
        'payments': payments,
        'today_calories': today_calories,
        'today_protein': round(today_protein, 1),
        'total_meals_count': total_meals_count,
        'total_workouts_count': total_workouts_count,
        'workout_streak': workout_streak,
        'recent_transactions': recent_transactions,
        'chart_months': json.dumps(chart_months),
        'chart_values': json.dumps(chart_values),
        'current_date': timezone.now(),
        'unread_notifications_count': unread_notifications_count,
        'active_challenge': active_challenge,
    }
    return render(request, 'siisto/index.html', context)



# ═══════════════════════════════════════════════════
#  CHATBOT — AI COACH (context-aware, multilingual)
# ═══════════════════════════════════════════════════

@login_required
def chatbot(request):
    from django.utils import translation
    profile = get_or_create_profile(request.user)
    chat_history = ChatMessage.objects.filter(user=request.user).order_by('date')

    today = timezone.now().date()
    today_message_count = ChatMessage.objects.filter(
        user=request.user, date__date=today
    ).count()
    is_limit_reached = (not profile.has_active_pro) and (today_message_count >= FREE_CHATBOT_DAILY_LIMIT)

    if request.method == "POST":
        user_message = request.POST.get('user_message', '').strip()
        is_ajax = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or
            'application/json' in request.headers.get('Accept', '') or
            request.POST.get('ajax') == 'true'
        )

        if not user_message:
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Empty message'}, status=400)
            return redirect('chatbot')

        if is_limit_reached:
            limit_msg = (
                'لقد استنفدت حدك اليومي المجاني (5 رسائل). قم بالترقية إلى برو للحصول على محادثات غير محدودة!'
                if profile.language == 'ar' else
                ('You have reached your free daily limit (5 messages). Upgrade to Pro for unlimited AI coach chat!'
                 if profile.language == 'en' else
                 'Maanta xadkaaga bilaashka ah ayaad gaadhay (5 fariin). Upgrade Pro si aad u hesho jawaabo aan xad lahayn!')
            )
            if is_ajax:
                return JsonResponse({
                    'status': 'limit_reached',
                    'message': limit_msg,
                    'upgrade_url': '/upgrade-pro/'
                })
            messages.warning(request, limit_msg)
            return redirect('chatbot')

        # --- Build rich, context-aware prompt ---
        # Recent conversation history (last 10 exchanges)
        recent_history = ChatMessage.objects.filter(
            user=request.user
        ).order_by('-date')[:10]
        history_text = ""
        for msg in reversed(list(recent_history)):
            history_text += f"User: {msg.message}\nAI: {msg.response}\n"

        # Recent workout context (last 7 days)
        week_ago = today - datetime.timedelta(days=7)
        recent_workouts = Workout.objects.filter(
            user=request.user, date__date__gte=week_ago
        ).order_by('-date')[:5]
        workout_context = ""
        if recent_workouts.exists():
            workout_list = ", ".join([f"{w.name} ({w.duration}min)" for w in recent_workouts])
            workout_context = f"Recent workouts this week: {workout_list}."

        # Recent meal context (today)
        today_meals = Meal.objects.filter(user=request.user, date__date=today).order_by('-date')[:5]
        meal_context = ""
        if today_meals.exists():
            meal_list = ", ".join([f"{m.name} ({m.calories}kcal, {m.protein}g protein)" for m in today_meals])
            total_cal = sum(m.calories for m in today_meals)
            total_prot = sum(m.protein for m in today_meals)
            meal_context = f"Today's logged meals: {meal_list} (Total: {total_cal} kcal, {total_prot:.1f}g protein)."

        # RAG: Search matching exercises in ExerciseLibrary based on user message keywords
        from django.db.models import Q
        user_words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', user_message.lower()) if w not in ['the', 'and', 'for', 'how', 'what', 'can', 'you', 'give', 'waan', 'waxaad', 'iyo']]
        rag_exercises = []
        if user_words:
            query_filter = Q()
            for w in user_words[:4]:
                query_filter |= Q(name__icontains=w) | Q(category__icontains=w) | Q(subcategory__icontains=w) | Q(target_muscle__icontains=w)
            matched_exs = ExerciseLibrary.objects.filter(query_filter)[:6]
            if matched_exs.exists():
                rag_exercises = [f"{e.name} ({e.category} / {e.subcategory} - {e.target_muscle})" for e in matched_exs]

        rag_exercise_context = ""
        if rag_exercises:
            rag_exercise_context = "Relevant database exercises: " + ", ".join(rag_exercises) + "."

        # Routine 90-Day Challenge Status
        active_challenge = Routine90.objects.filter(user=request.user, is_active=True).first()
        challenge_context = ""
        if active_challenge:
            challenge_context = f"90-Day Challenge: Day {active_challenge.current_day}/90 (Streak: {active_challenge.streak} days, Progress: {active_challenge.progress_percentage}%)."

        current_weight = profile.miisaan_hadda
        active_lang = profile.language or translation.get_language() or 'so'

        system_prompt = (
            f"You are Siisto AI Fitness & Health Coach — an elite, professional AI coach.\n"
            f"IMPORTANT: Respond in {active_lang.upper()} language naturally and professionally. "
            f"If user writes in Somali, answer in Somali. If in English, answer in English. If in Arabic, answer in Arabic.\n\n"
            f"USER PROFILE:\n"
            f"- Name: {request.user.first_name or request.user.username}\n"
            f"- Current weight: {current_weight or 'Unknown'} kg\n"
            f"- Target weight: {profile.miisaanka_yoolka or 'Unknown'} kg\n"
            f"- Height: {profile.dhererka or 'Unknown'} cm\n"
            f"- Age: {profile.da_da or 'Unknown'}\n"
            f"- Gender: {profile.jinsiga or 'Unknown'}\n"
            f"- Goal: {profile.hadafka or 'Unknown'}\n"
            f"- Activity Level: {profile.heerka_dhaqdhaqaaqa or 'Unknown'}\n"
            f"- Fitness Level: {profile.fitness_level or 'Unknown'}\n"
            f"- Pro Member: {'Yes' if profile.has_active_pro else 'No (Free)'}\n\n"
            f"APP DATABASE CONTEXT (RAG):\n"
            f"{workout_context}\n"
            f"{meal_context}\n"
            f"{challenge_context}\n"
            f"{rag_exercise_context}\n\n"
            f"CONVERSATION HISTORY:\n{history_text}\n\n"
            "INSTRUCTIONS:\n"
            "- Use the user profile, RAG database context, and conversation history to give accurate, personalized answers.\n"
            "- Recommend real exercises from the app database when relevant.\n"
            "- If user asks about sets/reps after discussing an exercise, connect directly to that exercise.\n"
            "- Format responses with bullet points, tables, and clean markdown.\n"
            "- Give detailed, expert-level advice with empathy and encouragement.\n"
        )

        ai_response = ask_gemini(
            user_message,
            custom_system_prompt=system_prompt,
            is_pro=profile.has_active_pro,
            language=active_lang,
            conversation_history=history_text,
        )

        msg_obj = ChatMessage.objects.create(
            user=request.user,
            message=user_message,
            response=ai_response
        )

        new_count = today_message_count + 1
        remaining = max(0, FREE_CHATBOT_DAILY_LIMIT - new_count) if not profile.has_active_pro else None

        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': user_message,
                'response': ai_response,
                'date': msg_obj.date.strftime('%I:%M %p'),
                'is_pro': profile.has_active_pro,
                'remaining_messages': remaining,
                'daily_limit': FREE_CHATBOT_DAILY_LIMIT if not profile.has_active_pro else None,
            })

        return redirect('chatbot')

    return render(request, 'siisto/chatbot.html', {
        'chat_history': chat_history,
        'profile': profile,
        'today_message_count': today_message_count,
        'daily_limit': FREE_CHATBOT_DAILY_LIMIT,
        'is_limit_reached': is_limit_reached,
        'remaining_messages': max(0, FREE_CHATBOT_DAILY_LIMIT - today_message_count) if not profile.has_active_pro else None,
    })


# ═══════════════════════════════════════════════════
#  PAYMENT / PRO UPGRADE — PAYPAL
# ═══════════════════════════════════════════════════

@login_required
def upgrade_pro(request):
    profile = get_or_create_profile(request.user)
    recent_payments = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'siisto/payment.html', {
        'profile': profile,
        'recent_payments': recent_payments,
        'price_monthly': PRO_PRICE_MONTHLY,
        'price_annual': PRO_PRICE_ANNUAL,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        'paypal_mode': settings.PAYPAL_MODE,
    })


@login_required
@require_POST
def paypal_create_order(request):
    """
    Step 1: Create a PayPal order and return the order ID to the frontend.
    The PayPal JS SDK uses this order ID to show the payment popup.
    """
    try:
        data = json.loads(request.body)
        plan_type = data.get('plan_type', 'monthly')
    except Exception:
        plan_type = request.POST.get('plan_type', 'monthly')

    amount = PRO_PRICE_ANNUAL if plan_type == 'annual' else PRO_PRICE_MONTHLY
    plan_name = 'Siisto Pro Annual' if plan_type == 'annual' else 'Siisto Pro Monthly'

    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        return JsonResponse({
            'status': 'error',
            'message': 'PayPal is not configured. Please contact support.'
        }, status=500)

    access_token = get_paypal_access_token()
    if not access_token:
        return JsonResponse({
            'status': 'error',
            'message': 'Could not connect to PayPal. Please try again.'
        }, status=503)

    # Internal transaction ID
    tx_id = f"SIISTO-{uuid.uuid4().hex[:12].upper()}"

    # Create PayPal order
    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "reference_id": tx_id,
            "description": f"{plan_name} - Siisto Fitness App",
            "amount": {
                "currency_code": "USD",
                "value": str(amount),
            },
            "custom_id": f"{request.user.id}:{plan_type}:{tx_id}",
        }],
        "application_context": {
            "brand_name": "Siisto Fitness",
            "user_action": "PAY_NOW",
            "return_url": request.build_absolute_uri('/upgrade-pro/'),
            "cancel_url": request.build_absolute_uri('/upgrade-pro/'),
        }
    }

    try:
        resp = requests.post(
            f"{settings.PAYPAL_API_BASE}/v2/checkout/orders",
            json=order_data,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            },
            timeout=15,
        )
        resp.raise_for_status()
        order = resp.json()
        paypal_order_id = order.get('id')

        # Save pending transaction
        PaymentTransaction.objects.create(
            user=request.user,
            plan_name=plan_name,
            plan_type=plan_type,
            amount=amount,
            currency='USD',
            payment_method='paypal',
            transaction_id=tx_id,
            paypal_order_id=paypal_order_id,
            status='pending',
        )

        return JsonResponse({
            'status': 'success',
            'order_id': paypal_order_id,
            'tx_id': tx_id,
        })

    except requests.HTTPError as e:
        logger.error(f"PayPal create order error: {e.response.text if e.response else e}")
        return JsonResponse({'status': 'error', 'message': 'PayPal order creation failed.'}, status=502)
    except Exception as e:
        logger.error(f"PayPal create order exception: {e}")
        return JsonResponse({'status': 'error', 'message': 'Unexpected error.'}, status=500)


@login_required
@require_POST
def paypal_capture_order(request, order_id):
    """
    Step 2: Capture the approved PayPal order.
    Called after the user approves payment in the PayPal popup.
    Verifies with PayPal, then activates Pro.
    """
    access_token = get_paypal_access_token()
    if not access_token:
        return JsonResponse({'status': 'error', 'message': 'PayPal connection failed.'}, status=503)

    try:
        resp = requests.post(
            f"{settings.PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture",
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            },
            timeout=15,
        )
        resp.raise_for_status()
        capture_data = resp.json()

        if capture_data.get('status') != 'COMPLETED':
            return JsonResponse({
                'status': 'error',
                'message': f"Payment not completed. Status: {capture_data.get('status')}"
            }, status=400)

        # Extract PayPal details
        purchase_unit = capture_data.get('purchase_units', [{}])[0]
        capture = purchase_unit.get('payments', {}).get('captures', [{}])[0]
        capture_id = capture.get('id', '')
        payer = capture_data.get('payer', {})
        payer_email = payer.get('email_address', '')
        custom_id = purchase_unit.get('reference_id', '')

        # Find and update transaction
        tx = PaymentTransaction.objects.filter(
            user=request.user, paypal_order_id=order_id
        ).first()

        if not tx:
            # Fallback: create if missing
            tx = PaymentTransaction(
                user=request.user,
                transaction_id=f"PP-{uuid.uuid4().hex[:10].upper()}",
                paypal_order_id=order_id,
            )

        tx.paypal_capture_id = capture_id
        tx.paypal_payer_email = payer_email
        tx.status = 'completed'
        tx.save()

        # Activate Pro membership
        profile = get_or_create_profile(request.user)
        days = 365 if tx.plan_type == 'annual' else 30
        profile.is_pro = True
        profile.pro_started_at = timezone.now()
        profile.pro_expires_at = timezone.now() + datetime.timedelta(days=days)
        profile.save()

        # Create success notification
        create_notification(
            request.user, 'premium',
            '🎉 Siisto Pro Activated!',
            f'Welcome to Pro! Your membership is active until {profile.pro_expires_at.strftime("%d %b %Y")}.',
            action_url='/profile/',
        )

        logger.info(f"PayPal payment completed: user={request.user.username}, capture={capture_id}, amount={tx.amount}")

        return JsonResponse({
            'status': 'success',
            'message': f'Hambalyo! Siisto Pro waa la firiyay. Waxay dhacaysaa {profile.pro_expires_at.strftime("%d %b %Y")}.',
            'tx_id': tx.transaction_id,
            'expires_at': profile.pro_expires_at.strftime('%d %b %Y'),
        })

    except requests.HTTPError as e:
        logger.error(f"PayPal capture error: {e.response.text if e.response else e}")
        # Update transaction to failed
        PaymentTransaction.objects.filter(
            user=request.user, paypal_order_id=order_id
        ).update(status='failed')
        return JsonResponse({'status': 'error', 'message': 'Payment capture failed.'}, status=502)
    except Exception as e:
        logger.error(f"PayPal capture exception: {e}")
        return JsonResponse({'status': 'error', 'message': 'Unexpected error during payment.'}, status=500)


@csrf_exempt
@require_POST
def paypal_webhook(request):
    """
    PayPal Webhook handler for server-side events.
    Handles: PAYMENT.CAPTURE.COMPLETED, BILLING.SUBSCRIPTION.CANCELLED
    """
    try:
        webhook_body = request.body
        event = json.loads(webhook_body)
        event_type = event.get('event_type', '')

        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            resource = event.get('resource', {})
            custom_id = resource.get('custom_id', '')
            capture_id = resource.get('id', '')
            amount = float(resource.get('amount', {}).get('value', 0))

            # Find transaction by capture ID or custom_id
            tx = PaymentTransaction.objects.filter(paypal_capture_id=capture_id).first()
            if tx and tx.status != 'completed':
                tx.status = 'completed'
                tx.paypal_webhook_event = event_type
                tx.save()
                # Ensure Pro is activated
                profile = get_or_create_profile(tx.user)
                if not profile.is_pro:
                    days = 365 if tx.plan_type == 'annual' else 30
                    profile.is_pro = True
                    profile.pro_expires_at = timezone.now() + datetime.timedelta(days=days)
                    profile.save()

        elif event_type in ('BILLING.SUBSCRIPTION.CANCELLED', 'PAYMENT.CAPTURE.REFUNDED'):
            # Handle cancellation / refund
            resource = event.get('resource', {})
            capture_id = resource.get('id', '')
            tx = PaymentTransaction.objects.filter(paypal_capture_id=capture_id).first()
            if tx:
                tx.status = 'cancelled' if 'CANCELLED' in event_type else 'refunded'
                tx.paypal_webhook_event = event_type
                tx.save()

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        logger.error(f"PayPal webhook error: {e}")
        return JsonResponse({'status': 'error'}, status=400)


@login_required
@require_POST
def process_payment(request):
    """
    EVC Plus / Zaad / Sahal / manual payment handler.
    Creates a PENDING transaction only — does NOT auto-activate Pro.
    Admin must manually verify and activate.
    """
    payment_method = request.POST.get('payment_method', 'other')
    phone_number = request.POST.get('phone_number', '').strip()
    plan_type = request.POST.get('plan_type', 'monthly')
    plan_name = request.POST.get('plan_name', 'Siisto Pro Monthly')
    amount = PRO_PRICE_ANNUAL if plan_type == 'annual' else PRO_PRICE_MONTHLY

    tx_id = f"TX-{uuid.uuid4().hex[:10].upper()}"

    PaymentTransaction.objects.create(
        user=request.user,
        plan_name=plan_name,
        plan_type=plan_type,
        amount=amount,
        currency='USD',
        payment_method=payment_method.lower().replace(' ', '_'),
        phone_number=phone_number,
        transaction_id=tx_id,
        status='pending',
        notes=f"Manual payment via {payment_method}. Awaiting admin verification.",
    )

    create_notification(
        request.user, 'premium',
        'Payment Pending Verification',
        f'Your {payment_method} payment of ${amount:.2f} is pending. We will verify and activate Pro within 24 hours. Ref: {tx_id}',
        action_url='/upgrade-pro/',
    )

    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        request.POST.get('ajax') == 'true'
    )
    if is_ajax:
        return JsonResponse({
            'status': 'pending',
            'message': f'Lacag-bixintaada ({payment_method}) waa la helay! Xafiiska Siisto ayaa xaqiijin doona 24 saacadood gudahood. Tix: {tx_id}',
            'tx_id': tx_id,
        })

    messages.info(
        request,
        f"✅ Lacag-bixintaada waa la helay! Waxaan xaqiijin doonaa 24 saacadood gudahood. Tix: {tx_id}"
    )
    return redirect('upgrade_pro')


# ═══════════════════════════════════════════════════
#  MEALS / NUTRITION
# ═══════════════════════════════════════════════════

@login_required
def add_meal(request):
    if request.method == "POST":
        name = request.POST.get('name') or "Healthy Meal"
        raw_calories = request.POST.get('calories', '').strip()
        raw_protein = request.POST.get('protein', '').strip()
        raw_carbs = request.POST.get('carbs', '').strip()
        raw_fats = request.POST.get('fats', '').strip()
        meal_type = request.POST.get('meal_type', 'lunch')
        notes = request.POST.get('notes', '').strip()
        image = request.FILES.get('meal_image')

        # Parse values, fall back to AI estimate if calories not provided
        try:
            cal_val = int(raw_calories) if raw_calories else None
            prot_val = float(raw_protein) if raw_protein else None
            carb_val = float(raw_carbs) if raw_carbs else None
            fat_val = float(raw_fats) if raw_fats else None
        except ValueError:
            cal_val = prot_val = carb_val = fat_val = None

        if cal_val is None:
            ai_macros = estimate_macros_with_gemini(name)
            cal_val = ai_macros['calories']
            prot_val = prot_val if prot_val is not None else ai_macros['protein']
            carb_val = carb_val if carb_val is not None else ai_macros['carbs']
            fat_val = fat_val if fat_val is not None else ai_macros['fats']
        else:
            prot_val = prot_val if prot_val is not None else 0.0
            carb_val = carb_val if carb_val is not None else 0.0
            fat_val = fat_val if fat_val is not None else 0.0

        Meal.objects.create(
            user=request.user,
            name=name,
            meal_type=meal_type,
            calories=cal_val,
            protein=prot_val,
            carbs=carb_val,
            fats=fat_val,
            image=image,
            notes=notes,
        )
        messages.success(request, f"Cuntada '{name}' si guul leh ayaa loo keydiyay! ({cal_val} kcal, {prot_val}g protein)")
        return redirect('add_meal')

    user_meals = Meal.objects.filter(user=request.user).order_by('-date')
    latest_meal = user_meals.first()
    profile = get_or_create_profile(request.user)
    return render(request, 'siisto/food.html', {
        'latest_meal': latest_meal,
        'user_meals': user_meals,
        'profile': profile,
    })


@login_required
@require_POST
def api_analyze_meal_photo(request):
    """
    Receives an uploaded meal photo, uses Gemini AI Vision to estimate macros.
    Free users: 2 scans/day. Pro users: Unlimited.
    """
    profile = get_or_create_profile(request.user)

    if not profile.has_active_pro:
        today = timezone.now().date()
        today_meal_count = Meal.objects.filter(user=request.user, date__date=today).count()
        if today_meal_count >= FREE_FOOD_SCAN_DAILY_LIMIT:
            return JsonResponse({
                'status': 'limit_reached',
                'message': f'Maanta {FREE_FOOD_SCAN_DAILY_LIMIT} scan oo bilaash ah ayaad isticmaalatay. Upgrade Pro!',
                'upgrade_url': '/upgrade-pro/'
            }, status=403)

    if 'meal_photo' not in request.FILES:
        return JsonResponse({'status': 'error', 'message': 'No meal photo uploaded'}, status=400)

    photo = request.FILES['meal_photo']
    estimate = analyze_meal_photo_with_gemini(photo)

    return JsonResponse({
        'status': 'success',
        'data': {
            'name': estimate.get('name', 'Analyzed Meal'),
            'calories': estimate.get('calories', 500),
            'protein': estimate.get('protein', 30.0),
            'carbs': estimate.get('carbs', 45.0),
            'fats': estimate.get('fats', 15.0),
            'description': estimate.get('description', ''),
            'is_estimate': True,
            'is_pro': profile.has_active_pro,
            'disclaimer': 'Qiyaastan waxaa soo saaray AI (Gemini Vision). Fadlan sax ama xaqiiji ka hor inta aadan keydin.',
        }
    })


@login_required
def edit_meal(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id, user=request.user)
    if request.method == "POST":
        meal.name = request.POST.get('name', meal.name)
        meal.meal_type = request.POST.get('meal_type', meal.meal_type)
        meal.notes = request.POST.get('notes', meal.notes)
        try:
            meal.calories = int(request.POST.get('calories', meal.calories))
            meal.protein = float(request.POST.get('protein', meal.protein))
            meal.carbs = float(request.POST.get('carbs', meal.carbs))
            meal.fats = float(request.POST.get('fats', meal.fats))
        except (ValueError, TypeError):
            pass
        meal.save()
        messages.success(request, "Xogta cuntada waa la cusbooneysiiyay!")
        return redirect('history')
    return render(request, 'siisto/edit_meal.html', {'meal': meal})


@login_required
def delete_meal(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id, user=request.user)
    if request.method == "POST":
        meal.delete()
        messages.success(request, "Cuntada waa la tirtiray!")
        return redirect('history')
    return render(request, 'siisto/confirm_delete.html', {'item_name': meal.name, 'type': 'meal'})


# ═══════════════════════════════════════════════════
#  WORKOUTS / GYM
# ═══════════════════════════════════════════════════

@login_required
def add_workout(request):
    exercises = ExerciseLibrary.objects.all().order_by('category', 'subcategory', 'name')
    categories = {}
    for ex in exercises:
        cat = ex.category
        sub = ex.subcategory or 'General'
        if cat not in categories:
            categories[cat] = {}
        if sub not in categories[cat]:
            categories[cat][sub] = []
        categories[cat][sub].append(ex)

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        duration = request.POST.get('duration', 15)
        sets = request.POST.get('sets', 4)
        reps = request.POST.get('reps', 10)
        weight_kg = request.POST.get('weight_kg', 0)
        body_part = request.POST.get('body_part', 'Other')
        notes = request.POST.get('notes', '').strip()
        exercise_id = request.POST.get('exercise_id')

        exercise_obj = None
        if exercise_id:
            try:
                exercise_obj = ExerciseLibrary.objects.get(id=int(exercise_id))
                if not name:
                    name = exercise_obj.name
                if not body_part or body_part == 'Other':
                    body_part = exercise_obj.category
            except (ExerciseLibrary.DoesNotExist, ValueError):
                pass

        if not name:
            name = "Workout Session"

        try:
            Workout.objects.create(
                user=request.user,
                name=name,
                exercise=exercise_obj,
                duration=int(duration),
                sets=int(sets),
                reps=int(reps),
                weight_kg=float(weight_kg),
                body_part=body_part,
                notes=notes,
                video_3d_url=exercise_obj.video_3d_url if exercise_obj else None,
            )
            messages.success(request, f"Jimicsiga '{name}' si guul leh ayaa loo diiwaangeliyay!")
        except Exception as e:
            logger.error(f"Workout save error: {e}")
            messages.error(request, "Khalad ayaa dhacay. Fadlan isku day mar kale.")

        return redirect('index')

    return render(request, 'siisto/gym.html', {
        'exercises': exercises,
        'categories': categories,
    })


@login_required
def exercise_detail(request, exercise_id):
    """Exercise detail page with local video player."""
    exercise = get_object_or_404(ExerciseLibrary, id=exercise_id)
    related = ExerciseLibrary.objects.filter(
        category=exercise.category
    ).exclude(id=exercise.id)[:6]
    return render(request, 'siisto/exercise_detail.html', {
        'exercise': exercise,
        'related_exercises': related,
    })


@staff_member_required
@require_POST
def api_update_exercise_video(request, exercise_id):
    """Staff-only: Updates, uploads, or deletes the video URL/file for an exercise."""
    exercise = get_object_or_404(ExerciseLibrary, id=exercise_id)

    if request.FILES.get('video_file'):
        exercise.video_file = request.FILES['video_file']
        exercise.save(update_fields=['video_file'])
        return JsonResponse({
            'status': 'success',
            'message': f"Video file uploaded for '{exercise.name}'.",
            'exercise_id': exercise.id,
            'video_url': exercise.video_file.url,
        })

    action = request.POST.get('action')
    if action == 'delete':
        exercise.video_file = None
        exercise.video_3d_url = ''
        exercise.save(update_fields=['video_file', 'video_3d_url'])
        return JsonResponse({
            'status': 'success',
            'message': f"Video removed for '{exercise.name}'.",
            'exercise_id': exercise.id,
        })

    try:
        data = json.loads(request.body)
        new_video_url = data.get('video_url', '').strip()
    except Exception:
        new_video_url = request.POST.get('video_url', '').strip()

    exercise.video_3d_url = new_video_url
    exercise.save(update_fields=['video_3d_url'])

    return JsonResponse({
        'status': 'success',
        'message': f"Video URL updated for '{exercise.name}'.",
        'exercise_id': exercise.id,
        'video_url': exercise.video_3d_url,
    })


@login_required
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == "POST":
        workout.name = request.POST.get('name', workout.name)
        workout.body_part = request.POST.get('body_part', workout.body_part)
        workout.notes = request.POST.get('notes', workout.notes)
        try:
            workout.duration = int(request.POST.get('duration', workout.duration))
            workout.sets = int(request.POST.get('sets', workout.sets))
            workout.reps = int(request.POST.get('reps', workout.reps))
            workout.weight_kg = float(request.POST.get('weight_kg', workout.weight_kg))
        except (ValueError, TypeError):
            pass
        workout.save()
        messages.success(request, "Jimicsiga waa la cusbooneysiiyay!")
        return redirect('history')
    return render(request, 'siisto/edit_workout.html', {'workout': workout})


@login_required
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == "POST":
        workout.delete()
        messages.success(request, "Jimicsiga waa la tirtiray!")
        return redirect('history')
    return render(request, 'siisto/confirm_delete.html', {'item_name': workout.name, 'type': 'workout'})


# ═══════════════════════════════════════════════════
#  AI FORM DETECTION
# ═══════════════════════════════════════════════════

@login_required
def ai_form_detection(request):
    profile = get_or_create_profile(request.user)
    exercises = ExerciseLibrary.objects.all().order_by('category', 'name')
    initial_exercise = request.GET.get('exercise', 'squat')
    
    categories = {}
    for ex in exercises:
        if ex.category not in categories:
            categories[ex.category] = []
        categories[ex.category].append(ex)

    return render(request, 'siisto/ai_form_detection.html', {
        'profile': profile,
        'exercises': exercises,
        'categories': categories,
        'initial_exercise': initial_exercise,
    })


# ═══════════════════════════════════════════════════
#  AI RECOMMENDATIONS (REAL GEMINI AI)
# ═══════════════════════════════════════════════════

@login_required
def workout_recommendation(request):
    """
    Real AI workout recommendation view using Gemini AI.
    Personalized using weight, goal, fitness level, activity level, and workout history.
    """
    profile = get_or_create_profile(request.user)
    recent_workouts = Workout.objects.filter(user=request.user).order_by('-date')[:10]
    weight_logs = WeightLog.objects.filter(user=request.user).order_by('-date')[:5]
    exercises = ExerciseLibrary.objects.all().order_by('category', 'name')[:30]

    current_weight = profile.miisaan_hadda
    weight_trend = ""
    if weight_logs.count() >= 2:
        logs = list(weight_logs)
        diff = logs[0].weight - logs[-1].weight
        if diff < 0:
            weight_trend = f"Weight is increasing (+{abs(diff):.1f}kg over last {weight_logs.count()} logs)"
        elif diff > 0:
            weight_trend = f"Weight is decreasing (-{diff:.1f}kg over last {weight_logs.count()} logs)"
        else:
            weight_trend = "Weight is stable"

    workout_history_text = ""
    if recent_workouts.exists():
        body_parts_trained = [w.body_part for w in recent_workouts if w.body_part]
        from collections import Counter
        body_part_freq = Counter(body_parts_trained).most_common(5)
        most_trained = ", ".join([f"{bp} ({cnt}x)" for bp, cnt in body_part_freq])
        workout_history_text = (
            f"Recent workouts ({recent_workouts.count()} logged): "
            f"Most trained body parts: {most_trained}. "
            f"Last workout: {recent_workouts.first().name if recent_workouts.first() else 'None'}."
        )

    available_exercises_text = ", ".join([f"{e.name} ({e.category})" for e in exercises])

    workout_prompt = (
        f"You are an elite AI fitness coach at Siisto. Generate a comprehensive, highly personalized 7-DAY WORKOUT PLAN.\n\n"
        f"USER PROFILE:\n"
        f"- Goal: {profile.hadafka or 'general fitness'}\n"
        f"- Age: {profile.da_da or 'unknown'}\n"
        f"- Gender: {profile.jinsiga or 'unknown'}\n"
        f"- Current weight: {current_weight or 'unknown'} kg\n"
        f"- Target weight: {profile.miisaanka_yoolka or 'unknown'} kg\n"
        f"- Height: {profile.dhererka or 'unknown'} cm\n"
        f"- Activity level: {profile.heerka_dhaqdhaqaaqa or 'moderate'}\n"
        f"- Fitness level: {profile.fitness_level or 'beginner'}\n"
        f"- Experience: {profile.experience_level or 'none'}\n"
        f"- Weight trend: {weight_trend}\n"
        f"- {workout_history_text}\n\n"
        f"AVAILABLE GYM EXERCISES: {available_exercises_text}\n\n"
        "INSTRUCTIONS:\n"
        "1. Generate a structured 7-day schedule (Monday to Sunday) with rest days included.\n"
        "2. For each workout day: list exercise names, target muscles, sets, reps, and rest intervals.\n"
        "3. Include warm-up, proper form cues, and cool-down instructions.\n"
        "4. Detail progressive overload strategy for the coming weeks.\n"
        "5. Explain why these specific exercises match the user's goal.\n"
        "6. Use clean markdown formatting (headers, tables, bullet points).\n"
        f"7. Respond in {profile.preferred_language.upper()} language.\n"
    )

    recommendation_text = ask_gemini(
        workout_prompt,
        is_pro=profile.has_active_pro,
        language=profile.preferred_language,
    )

    today = timezone.now().date()
    today_meals = Meal.objects.filter(user=request.user, date__date=today)
    total_cals_today = today_meals.aggregate(Sum('calories'))['calories__sum'] or 0
    total_protein_today = today_meals.aggregate(Sum('protein'))['protein__sum'] or 0.0

    return render(request, 'siisto/ai_recommendation.html', {
        'page_title': 'AI Workout Plan & Recommendation',
        'recommendation': recommendation_text,
        'profile': profile,
        'total_cals_today': total_cals_today,
        'total_protein_today': total_protein_today,
    })


@login_required
def meal_recommendation(request):
    """
    Real AI meal recommendation view using Gemini AI.
    Personalized using weight, goal, activity level, and nutrition history.
    """
    profile = get_or_create_profile(request.user)
    recent_meals = Meal.objects.filter(user=request.user).order_by('-date')[:10]
    current_weight = profile.miisaan_hadda

    meal_history_text = ""
    if recent_meals.exists():
        avg_cal = recent_meals.aggregate(Avg('calories'))['calories__avg'] or 0
        avg_protein = recent_meals.aggregate(Avg('protein'))['protein__avg'] or 0
        meal_history_text = (
            f"Recent meals logged ({recent_meals.count()} items): "
            f"Avg calories: {int(avg_cal)} kcal, Avg protein: {int(avg_protein)}g."
        )

    meal_prompt = (
        f"You are an expert AI sports nutritionist at Siisto. Generate a detailed, highly personalized 7-DAY MEAL & NUTRITION PLAN.\n\n"
        f"USER PROFILE:\n"
        f"- Goal: {profile.hadafka or 'general health'}\n"
        f"- Current weight: {current_weight or 'unknown'} kg\n"
        f"- Target weight: {profile.miisaanka_yoolka or 'unknown'} kg\n"
        f"- Height: {profile.dhererka or 'unknown'} cm\n"
        f"- Age: {profile.da_da or 'unknown'}\n"
        f"- Gender: {profile.jinsiga or 'unknown'}\n"
        f"- Activity level: {profile.heerka_dhaqdhaqaaqa or 'moderate'}\n"
        f"- Fitness level: {profile.fitness_level or 'beginner'}\n"
        f"- {meal_history_text}\n\n"
        "INSTRUCTIONS:\n"
        "1. Calculate recommended daily target calories and macros (Protein, Carbs, Fats).\n"
        "2. Detail a full 7-day meal plan: Breakfast, Lunch, Dinner, and Healthy Snacks.\n"
        "3. Provide exact macro breakdown (calories, protein g, carbs g, fats g) per meal in markdown tables.\n"
        "4. Include popular/accessible Somali and international healthy foods (chicken, fish, eggs, oats, beans, rice, vegetables, fruits).\n"
        "5. Include hydration guidelines and supplement advice (if appropriate).\n"
        "6. Provide an easy weekly grocery shopping checklist.\n"
        f"7. Respond in {profile.preferred_language.upper()} language.\n"
    )

    recommendation_text = ask_gemini(
        meal_prompt,
        is_pro=profile.has_active_pro,
        language=profile.preferred_language,
    )

    today = timezone.now().date()
    today_meals = Meal.objects.filter(user=request.user, date__date=today)
    total_cals_today = today_meals.aggregate(Sum('calories'))['calories__sum'] or 0
    total_protein_today = today_meals.aggregate(Sum('protein'))['protein__sum'] or 0.0

    return render(request, 'siisto/ai_recommendation.html', {
        'page_title': 'AI Meal Plan & Nutrition',
        'recommendation': recommendation_text,
        'profile': profile,
        'total_cals_today': total_cals_today,
        'total_protein_today': total_protein_today,
    })


@login_required
def ai_recommendation(request):
    """
    Unified entry point for AI recommendations.
    Routes to meal_recommendation if type='meal', otherwise workout_recommendation.
    """
    rec_type = request.GET.get('type', 'workout')
    if rec_type == 'meal':
        return meal_recommendation(request)
    return workout_recommendation(request)


# ═══════════════════════════════════════════════════
#  HISTORY
# ═══════════════════════════════════════════════════

@login_required
def history(request):
    meals = Meal.objects.filter(user=request.user).order_by('-date')
    workouts = Workout.objects.filter(user=request.user).order_by('-date')
    payments = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')
    profile = get_or_create_profile(request.user)
    return render(request, 'siisto/history.html', {
        'cuntooyinka': meals,
        'jimicsiyada': workouts,
        'payments': payments,
        'profile': profile,
    })


# ═══════════════════════════════════════════════════
#  PROGRESS & STATISTICS
# ═══════════════════════════════════════════════════

@login_required
def progress_view(request):
    profile = get_or_create_profile(request.user)

    total_meals = Meal.objects.filter(user=request.user).count()
    total_workouts = Workout.objects.filter(user=request.user).count()
    workout_streak = get_workout_streak(request.user)

    # Weight chart data (last 30 entries)
    weight_logs = WeightLog.objects.filter(user=request.user).order_by('date')[:30]
    weight_dates = [log.date.strftime('%d %b') for log in weight_logs]
    weight_values = [log.weight for log in weight_logs]

    # Body part breakdown
    body_parts = (
        Workout.objects
        .filter(user=request.user)
        .values('body_part')
        .annotate(count=Count('id'))
        .order_by('-count')[:8]
    )

    # Monthly calorie trend (last 8 weeks)
    calorie_trend = []
    for i in range(7, -1, -1):
        week_start = (timezone.now() - datetime.timedelta(weeks=i)).date()
        week_end = week_start + datetime.timedelta(days=7)
        total = Meal.objects.filter(
            user=request.user,
            date__date__gte=week_start,
            date__date__lt=week_end,
        ).aggregate(Sum('calories'))['calories__sum'] or 0
        calorie_trend.append({
            'week': week_start.strftime('%d %b'),
            'calories': total,
        })

    # Workout duration trend (last 30 days)
    daily_workouts = (
        Workout.objects
        .filter(user=request.user)
        .annotate(day=TruncDate('date'))
        .values('day')
        .annotate(total_duration=Sum('duration'), count=Count('id'))
        .order_by('-day')[:14]
    )

    # 90-day challenge
    active_challenge = Routine90.objects.filter(user=request.user, is_active=True).first()

    # Goal progress (weight) — safe float casting to prevent TypeError
    goal_progress = None
    current_weight = profile.miisaan_hadda
    try:
        raw_goal = profile.miisaanka_yoolka
        goal_weight = float(raw_goal) if raw_goal not in (None, '', 'target_weight', 'None') else None
    except (TypeError, ValueError):
        goal_weight = None

    if current_weight and goal_weight:
        try:
            initial_logs = WeightLog.objects.filter(user=request.user).order_by('date').first()
            start_weight = float(initial_logs.weight) if initial_logs else float(current_weight)
            total_needed = abs(start_weight - goal_weight)
            progress_made = abs(start_weight - float(current_weight))
            goal_progress = min(int((progress_made / total_needed) * 100), 100) if total_needed > 0 else 0
        except (TypeError, ValueError, ZeroDivisionError):
            goal_progress = None

    return render(request, 'siisto/progress.html', {
        'total_meals': total_meals,
        'total_workouts': total_workouts,
        'workout_streak': workout_streak,
        'profile': profile,
        'weight_logs': weight_logs,
        'weight_dates': json.dumps(weight_dates),
        'weight_values': json.dumps(weight_values),
        'body_parts': list(body_parts),
        'calorie_trend': calorie_trend,
        'daily_workouts': list(daily_workouts),
        'active_challenge': active_challenge,
        'goal_progress': goal_progress,
        'current_weight': current_weight,
    })


# ═══════════════════════════════════════════════════
#  90-DAY CHALLENGE
# ═══════════════════════════════════════════════════

@login_required
def challenge_90day(request):
    profile = get_or_create_profile(request.user)
    challenge = Routine90.objects.filter(user=request.user, is_active=True).first()
    all_challenges = Routine90.objects.filter(user=request.user).order_by('-date')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'start' and not challenge:
            start_date = timezone.now().date()
            challenge = Routine90.objects.create(
                user=request.user,
                title='90-Day Fitness Challenge',
                is_active=True,
                start_date=start_date,
                current_day=1,
                streak=0,
            )
            create_notification(
                request.user, 'challenge',
                '🔥 90-Day Challenge Started!',
                'You have started the 90-Day Fitness Challenge. Keep it going!',
                action_url='/90-day-challenge/',
            )
            messages.success(request, "🔥 90-Day Challenge waa la bilaabay! Guul!")
            return redirect('challenge_90day')

        elif action == 'complete_day' and challenge:
            today = timezone.now().date()
            if challenge.last_activity_date != today:
                prev_activity_date = challenge.last_activity_date
                challenge.last_activity_date = today
                if prev_activity_date and (today - prev_activity_date).days == 1:
                    challenge.streak += 1
                else:
                    challenge.streak = 1
                challenge.current_day = min(challenge.current_day + 1, 90)
                challenge.longest_streak = max(challenge.streak, challenge.longest_streak)
                if challenge.current_day >= 90:
                    challenge.completed = True
                    challenge.is_active = False
                    create_notification(
                        request.user, 'achievement',
                        '🏆 90-Day Challenge Completed!',
                        'Incredible! You completed the 90-Day Fitness Challenge!',
                    )
                challenge.save()
                messages.success(request, f"Maalin {challenge.current_day} ayaad dhamaystirtay! 🎯 Streak: {challenge.streak}")
            else:
                messages.info(request, "Maantaad horay u dhamaystirtay!")
            return redirect('challenge_90day')

        elif action == 'reset' and challenge:
            challenge.is_active = False
            challenge.save()
            messages.info(request, "Challenge waa la joojiyay.")
            return redirect('challenge_90day')

    # Build calendar grid (90 days)
    calendar_days = []
    if challenge and challenge.start_date:
        today = timezone.now().date()
        for day_num in range(1, 91):
            day_date = challenge.start_date + datetime.timedelta(days=day_num - 1)
            has_workout = Workout.objects.filter(
                user=request.user, date__date=day_date
            ).exists()
            is_today = day_date == today
            is_past = day_date < today
            calendar_days.append({
                'day': day_num,
                'date': day_date,
                'completed': has_workout,
                'is_today': is_today,
                'is_future': day_date > today,
            })

    return render(request, 'siisto/challenge.html', {
        'challenge': challenge,
        'all_challenges': all_challenges,
        'calendar_days': calendar_days,
        'profile': profile,
    })


@login_required
@require_POST
def api_complete_challenge_day(request):
    challenge = Routine90.objects.filter(user=request.user, is_active=True).first()
    if not challenge:
        return JsonResponse({'status': 'error', 'message': 'No active challenge'}, status=404)

    today = timezone.now().date()
    if challenge.last_activity_date == today:
        return JsonResponse({
            'status': 'already_done',
            'message': 'Maanta horay u dhamaystirtay!',
            'current_day': challenge.current_day,
            'streak': challenge.streak,
        })

    challenge.last_activity_date = today
    challenge.streak = (challenge.streak + 1)
    challenge.current_day = min(challenge.current_day + 1, 90)
    challenge.longest_streak = max(challenge.streak, challenge.longest_streak)
    if challenge.current_day >= 90:
        challenge.completed = True
        challenge.is_active = False
    challenge.save()

    return JsonResponse({
        'status': 'success',
        'message': f'Maalin {challenge.current_day} dhamaystay! Streak: {challenge.streak}',
        'current_day': challenge.current_day,
        'streak': challenge.streak,
        'progress': challenge.progress_percentage,
    })


# ═══════════════════════════════════════════════════
#  PROFILE
# ═══════════════════════════════════════════════════

@login_required
def profile_view(request):
    profile = get_or_create_profile(request.user)

    if request.method == "POST":
        action = request.POST.get('action', 'profile')

        # Handle form field name aliases from templates
        if request.POST.get('weight_submit'):
            action = 'weight'
        elif request.POST.get('goal_submit'):
            action = 'goal'

        if action == 'weight':
            # Support both 'weight' (from profile form action) and 'miisaanka' (from template field)
            weight_val = (request.POST.get('weight') or request.POST.get('miisaanka') or '').strip()
            if weight_val:
                try:
                    w = float(weight_val)
                    WeightLog.objects.create(user=request.user, weight=w)
                    messages.success(request, f"Miisaanka {w}kg waa la keydiyay!")
                except ValueError:
                    messages.error(request, "Fadlan geli miisaan saxsan.")
            return redirect('profile')

        elif action == 'goal':
            goal_val = (request.POST.get('miisaanka_yoolka') or '').strip()
            if goal_val:
                try:
                    profile.miisaanka_yoolka = float(goal_val)
                    profile.save(update_fields=['miisaanka_yoolka'])
                    messages.success(request, "Yoolka miisaanka waa la cusbooneysiiyay!")
                except ValueError:
                    messages.error(request, "Fadlan geli miisaan saxsan.")
            return redirect('profile')

        elif action == 'profile':
            # Full profile update
            profile.dhererka = request.POST.get('dhererka') or profile.dhererka
            profile.da_da = request.POST.get('da_da') or profile.da_da
            profile.jinsiga = request.POST.get('jinsiga') or profile.jinsiga
            profile.hadafka = request.POST.get('hadafka') or profile.hadafka
            profile.heerka_dhaqdhaqaaqa = request.POST.get('heerka_dhaqdhaqaaqa') or profile.heerka_dhaqdhaqaaqa
            profile.miisaanka_yoolka = request.POST.get('miisaanka_yoolka') or profile.miisaanka_yoolka
            profile.fitness_level = request.POST.get('fitness_level') or profile.fitness_level
            profile.experience_level = request.POST.get('experience_level') or profile.experience_level
            profile.bio = request.POST.get('bio', profile.bio)
            profile.location = request.POST.get('location', profile.location)
            
            # Language preference update
            pref_lang = request.POST.get('preferred_language') or request.POST.get('language')
            if pref_lang and pref_lang in ['so', 'en', 'ar']:
                profile.preferred_language = pref_lang
                translation.activate(pref_lang)
                request.session[LANGUAGE_SESSION_KEY] = pref_lang

            birth_date = request.POST.get('birth_date', '')
            if birth_date:
                try:
                    from datetime import date
                    profile.birth_date = date.fromisoformat(birth_date)
                except ValueError:
                    pass

            # Update numeric fields safely
            for field in ['dhererka', 'miisaanka_yoolka']:
                val = request.POST.get(field, '').strip()
                if val:
                    try:
                        setattr(profile, field, float(val))
                    except ValueError:
                        pass
            for field in ['da_da']:
                val = request.POST.get(field, '').strip()
                if val:
                    try:
                        setattr(profile, field, int(val))
                    except ValueError:
                        pass

            # Email update
            email = request.POST.get('email', '').strip()
            if email and email != request.user.email:
                request.user.email = email
                request.user.save()

            profile.save()
            messages.success(request, "Xogta profile-ka waa la cusbooneysiiyay!")
            resp = redirect('profile')
            if pref_lang and pref_lang in ['so', 'en', 'ar']:
                resp.set_cookie(settings.LANGUAGE_COOKIE_NAME, pref_lang, max_age=365*24*60*60)
            return resp

    weight_logs = WeightLog.objects.filter(user=request.user).order_by('-date')[:20]
    payments = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')

    # Weight chart
    weight_chart_dates = [log.date.strftime('%d %b') for log in reversed(list(weight_logs))]
    weight_chart_values = [log.weight for log in reversed(list(weight_logs))]

    return render(request, 'siisto/profile.html', {
        'profile': profile,
        'weight_logs': weight_logs,
        'payments': payments,
        'weight_chart_dates': json.dumps(weight_chart_dates),
        'weight_chart_values': json.dumps(weight_chart_values),
    })


# ═══════════════════════════════════════════════════
#  REGISTRATION & AUTH
# ═══════════════════════════════════════════════════

def login_view(request):
    """
    Handles user login using either username OR email address (case-insensitive).
    """
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        login_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not login_input or not password:
            messages.error(request, "Fadlan geli magacaaga ama email-kaaga iyo furaha sirta ah.")
            return render(request, 'registration/login.html')

        # Try custom backend first (email or username), then fallback
        from siisto.backends import EmailOrUsernameModelBackend
        backend = EmailOrUsernameModelBackend()
        user = backend.authenticate(request, username=login_input, password=password)

        if user is None:
            messages.error(request, "Magaca/Email-ka ama furaha sirta ah waa qaldan yahay. Fadlan dib u hubi.")
            return render(request, 'registration/login.html')

        if not user.is_active:
            messages.error(request, "Koontadaada waa la xidhay. La xiriir taageerada.")
            return render(request, 'registration/login.html')

        # Login with explicit backend to avoid backend mismatch errors
        login(request, user, backend='siisto.backends.EmailOrUsernameModelBackend')

        # Sync user's saved language preference into session
        try:
            profile = get_or_create_profile(user)
            lang = profile.preferred_language or 'so'
            request.session[LANGUAGE_SESSION_KEY] = lang
            request.session['_language'] = lang
            from django.utils import translation
            translation.activate(lang)
        except Exception:
            pass

        messages.success(request, f"Ku soo dhowow Siisto, {user.first_name or user.username}!")
        next_url = request.POST.get('next') or request.GET.get('next') or 'index'
        response = redirect(next_url)
        try:
            cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
            if hasattr(user, 'profile') and user.profile.preferred_language:
                response.set_cookie(cookie_name, user.profile.preferred_language, max_age=365*24*60*60)
        except Exception:
            pass
        return response

    return render(request, 'registration/login.html')


def logout_view(request):
    """
    Logs out the user cleanly and redirects to login.
    """
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, "Waad ka baxday nidaamka.")
    return redirect('login')


def register(request):
    """
    Registers a new user, automatically logging them in with their preferred language.
    """
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        first_name = request.POST.get('first_name', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        # Read preferred language from session or cookie
        preferred_lang = (
            request.session.get(LANGUAGE_SESSION_KEY)
            or request.COOKIES.get(getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language'))
            or 'so'
        )
        if preferred_lang not in ['so', 'en', 'ar']:
            preferred_lang = 'so'

        # Validate inputs
        error = None
        if not username or not password:
            error = "Fadlan buuxi dhammaan meelaha banaan."
        elif len(username) < 3:
            error = "Magaca isticmaalaha waa inuu ahaadaa ugu yaraan 3 xaraf."
        elif not re.match(r'^[a-zA-Z0-9_@.+-]+$', username):
            error = "Magaca isticmaalaha waxaa ku jiri kara xarfo, tiro, iyo _@.+- kaliya."
        elif password != password_confirm:
            error = "Furaha sirta ah isma laha (Passwords do not match)."
        elif len(password) < 6:
            error = "Furaha sirta ah waa inuu ka dheer yahay 6 xaraf."
        elif User.objects.filter(username__iexact=username).exists():
            error = "Magacan horay ayaa loo qaatay. Fadlan mid kale dooro."
        elif email and User.objects.filter(email__iexact=email).exists():
            error = "Email-kan horay ayaa loo isticmaalay. Fadlan soo gal ama email kale isticmaal."

        if error:
            messages.error(request, error)
            return render(request, 'registration/signup.html')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
            )
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.preferred_language = preferred_lang
            profile.save()

            # Log the user in immediately after registration
            login(request, user, backend='siisto.backends.EmailOrUsernameModelBackend')
            request.session[LANGUAGE_SESSION_KEY] = preferred_lang
            request.session['_language'] = preferred_lang
            request.session.save()
            from django.utils import translation
            translation.activate(preferred_lang)

            create_notification(
                user, 'system',
                f'Welcome to Siisto, {user.first_name or user.username}! 🎉',
                'Complete your profile and start your fitness journey.',
                action_url='/onboarding/',
            )
            messages.success(request, f"Ku soo dhowow Siisto Fitness, {user.username}!")
            response = redirect('onboarding_3d')
            cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
            response.set_cookie(cookie_name, preferred_lang, max_age=365*24*60*60)
            return response
        except Exception as e:
            logger.error(f"Registration error for '{username}': {e}")
            messages.error(request, "Dhibaato baa dhacday. Fadlan mar kale isku day.")

    return render(request, 'registration/signup.html')


# ═══════════════════════════════════════════════════
#  ONBOARDING
# ═══════════════════════════════════════════════════

def onboarding_3d(request):
    profile = None
    initial_data = {
        'weight': 70.0, 'height': 175.0, 'age': 25, 'gender': 'male',
        'goal': 'lose_weight', 'activity_level': 'moderate', 'target_weight': 65.0,
        'email': request.user.email if request.user.is_authenticated else '',
    }

    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        latest_weight = profile.miisaan_hadda
        if latest_weight:
            initial_data['weight'] = latest_weight
        if profile.dhererka:
            initial_data['height'] = profile.dhererka
        if profile.da_da:
            initial_data['age'] = profile.da_da
        if profile.jinsiga:
            initial_data['gender'] = profile.jinsiga
        if profile.hadafka:
            initial_data['goal'] = profile.hadafka
        if profile.heerka_dhaqdhaqaaqa:
            initial_data['activity_level'] = profile.heerka_dhaqdhaqaaqa
        if profile.miisaanka_yoolka:
            initial_data['target_weight'] = profile.miisaanka_yoolka

    return render(request, 'siisto/onboarding_3d.html', {
        'profile': profile,
        'initial_data': json.dumps(initial_data),
        'CURRENT_LANGUAGE': (profile.preferred_language if profile else None) or 'so',
    })


@require_POST
def api_save_onboarding(request):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST

        weight = float(data.get('weight', 70))
        height = float(data.get('height', 175))
        age = int(data.get('age', 25))
        gender = str(data.get('gender', 'male')).lower()
        goal = str(data.get('goal', 'lose_weight'))
        activity_level = str(data.get('activity_level', 'moderate'))
        target_weight = float(data.get('target_weight', weight))
        email = str(data.get('email', '')).strip()

        height_m = max(height / 100.0, 0.5)
        bmi = round(weight / (height_m * height_m), 1)
        if bmi < 18.5:
            bmi_status = "Miisaan Hooseeya (Underweight)"
            bmi_color = "#38bdf8"
        elif bmi < 25.0:
            bmi_status = "Miisaan Caafimaad Leh (Healthy)"
            bmi_color = "#4ade80"
        elif bmi < 30.0:
            bmi_status = "Miisaan Zaa'id (Overweight)"
            bmi_color = "#fbbf24"
        else:
            bmi_status = "Cayil Sare (Obese)"
            bmi_color = "#f87171"

        if gender == 'female':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        bmr = round(bmr)

        activity_multipliers = {
            'sedentary': 1.2, 'moderate': 1.45, 'active': 1.725, 'very_active': 1.9
        }
        mult = activity_multipliers.get(activity_level, 1.45)
        tdee = round(bmr * mult)

        if goal in ['lose_weight', 'fat_loss']:
            target_calories = max(int(tdee - 450), 1200)
            protein_factor = 2.0
            goal_label = "Miisaan Dhimis (Fat Loss)"
        elif goal in ['build_muscle', 'muscle_gain']:
            target_calories = int(tdee + 350)
            protein_factor = 2.2
            goal_label = "Muruq Dhis (Muscle Gain)"
        elif goal in ['athletic_endurance', 'fitness']:
            target_calories = int(tdee + 100)
            protein_factor = 1.8
            goal_label = "Jir Dhis & Awood (Fitness)"
        else:
            target_calories = int(tdee)
            protein_factor = 1.6
            goal_label = "Caafimaad Guud (Longevity)"

        water_liters = round(weight * 0.035, 1)
        protein_g = int(weight * protein_factor)
        fats_g = int((target_calories * 0.25) / 9)
        carbs_g = max(int((target_calories - (protein_g * 4 + fats_g * 9)) / 4), 50)
        diff = abs(weight - target_weight)
        estimated_weeks = max(int(diff / 0.5), 1) if diff > 0.5 else 4

        pref_lang = str(data.get('language', '')).strip().lower()
        if pref_lang in ['so', 'en', 'ar']:
            from django.utils import translation as trans_util
            trans_util.activate(pref_lang)
            request.session[LANGUAGE_SESSION_KEY] = pref_lang
            request.session['_language'] = pref_lang

        if request.user.is_authenticated:
            if email and not request.user.email:
                request.user.email = email
                request.user.save()

            profile, _ = Profile.objects.get_or_create(user=request.user)
            profile.dhererka = height
            profile.da_da = age
            profile.jinsiga = gender
            profile.hadafka = goal
            profile.heerka_dhaqdhaqaaqa = activity_level
            profile.miisaanka_yoolka = target_weight
            profile.onboarding_completed = True
            if pref_lang in ['so', 'en', 'ar']:
                profile.preferred_language = pref_lang
            profile.save()

            WeightLog.objects.create(user=request.user, weight=weight)

        res = JsonResponse({
            'status': 'success',
            'saved_to_db': request.user.is_authenticated,
            'metrics': {
                'bmi': bmi,
                'bmi_status': bmi_status,
                'bmi_color': bmi_color,
                'bmr': int(bmr),
                'tdee': int(tdee),
                'target_calories': target_calories,
                'water_liters': water_liters,
                'protein_g': protein_g,
                'carbs_g': carbs_g,
                'fats_g': fats_g,
                'estimated_weeks': estimated_weeks,
                'goal_label': goal_label,
                'weight': weight,
                'height': height,
                'target_weight': target_weight,
            },
            'redirect_url': '/progress/' if request.user.is_authenticated else '/signup/'
        })
        if pref_lang in ['so', 'en', 'ar']:
            cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
            res.set_cookie(cookie_name, pref_lang, max_age=365*24*60*60)
        return res
    except Exception as e:
        logger.error(f"Onboarding save error: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ═══════════════════════════════════════════════════
#  NOTIFICATIONS
# ═══════════════════════════════════════════════════

@login_required
@require_GET
def api_get_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user, is_read=False
    ).order_by('-created_at')[:10]
    return JsonResponse({
        'status': 'success',
        'count': notifications.count(),
        'notifications': [
            {
                'id': n.id,
                'type': n.notification_type,
                'title': n.title,
                'message': n.message,
                'action_url': n.action_url,
                'created_at': n.created_at.strftime('%d %b, %I:%M %p'),
            }
            for n in notifications
        ]
    })


@login_required
@require_POST
def api_mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def api_mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})


# ═══════════════════════════════════════════════════
#  ADMIN DASHBOARD
# ═══════════════════════════════════════════════════

@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    pro_users = Profile.objects.filter(is_pro=True).count()
    free_users = total_users - pro_users
    total_meals = Meal.objects.count()
    total_workouts = Workout.objects.count()
    total_revenue = PaymentTransaction.objects.filter(status='completed').aggregate(
        Sum('amount'))['amount__sum'] or 0
    total_transactions = PaymentTransaction.objects.filter(status='completed').count()
    pending_transactions = PaymentTransaction.objects.filter(status='pending').count()

    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_payments = PaymentTransaction.objects.select_related('user').order_by('-created_at')[:10]
    recent_meals = Meal.objects.select_related('user').order_by('-date')[:8]
    recent_workouts = Workout.objects.select_related('user').order_by('-date')[:8]

    from django.db.models.functions import TruncMonth
    monthly_revenue = (
        PaymentTransaction.objects
        .filter(status='completed')
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-month')[:6]
    )

    # Exercise stats
    total_exercises = ExerciseLibrary.objects.count()
    exercises_with_video = ExerciseLibrary.objects.filter(video_file__isnull=False).exclude(video_file='').count()
    active_challenges = Routine90.objects.filter(is_active=True).count()
    total_notifications = Notification.objects.filter(is_read=False).count()

    return render(request, 'siisto/admin_dashboard.html', {
        'total_users': total_users,
        'pro_users': pro_users,
        'free_users': free_users,
        'total_meals': total_meals,
        'total_workouts': total_workouts,
        'total_revenue': total_revenue,
        'total_transactions': total_transactions,
        'pending_transactions': pending_transactions,
        'recent_users': recent_users,
        'recent_payments': recent_payments,
        'recent_meals': recent_meals,
        'recent_workouts': recent_workouts,
        'monthly_revenue': list(monthly_revenue),
        'total_exercises': total_exercises,
        'exercises_with_video': exercises_with_video,
        'active_challenges': active_challenges,
        'total_notifications': total_notifications,
    })


# ═══════════════════════════════════════════════════
#  LANGUAGE SWITCHER
# ═══════════════════════════════════════════════════

def set_language_preference(request, lang_code=None):
    """
    Switches active language for the entire system across session, cookie, and user Profile.
    Supports JSON/fetch payloads, form submissions, and GET query parameters.
    """
    if not lang_code:
        if request.content_type == 'application/json' and request.body:
            try:
                body = json.loads(request.body.decode('utf-8'))
                lang_code = body.get('language') or body.get('lang')
            except Exception:
                pass
        if not lang_code:
            lang_code = (
                request.POST.get('language')
                or request.GET.get('lang')
                or request.GET.get('language')
                or 'so'
            )

    lang_code = str(lang_code)[:2].lower()
    if lang_code not in ['so', 'en', 'ar']:
        lang_code = 'so'

    from django.utils import translation
    translation.activate(lang_code)

    if hasattr(request, 'session'):
        request.session['_language'] = lang_code
        request.session[LANGUAGE_SESSION_KEY] = lang_code
        request.session[getattr(translation, 'LANGUAGE_SESSION_KEY', '_language')] = lang_code

    if request.user.is_authenticated:
        try:
            profile = get_or_create_profile(request.user)
            profile.preferred_language = lang_code
            profile.save(update_fields=['preferred_language'])
        except Exception as e:
            logger.warning(f"Could not persist language preference to profile: {e}")

    cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')

    # Return JSON for AJAX/fetch requests
    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or request.content_type == 'application/json'
        or request.GET.get('format') == 'json'
    )
    if is_ajax:
        res = JsonResponse({'status': 'success', 'language': lang_code})
        res.set_cookie(cookie_name, lang_code, max_age=365 * 24 * 60 * 60, samesite='Lax')
        return res

    next_url = (
        request.POST.get('next')
        or request.GET.get('next')
        or request.META.get('HTTP_REFERER')
        or '/'
    )
    response = redirect(next_url)
    response.set_cookie(cookie_name, lang_code, max_age=365 * 24 * 60 * 60, samesite='Lax')
    return response