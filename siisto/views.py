import json
import uuid
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.db.models import Sum, Count
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

from .models import (
    Meal, Workout, ChatMessage, ExerciseLibrary, 
    WeightLog, Profile, PaymentTransaction
)
from .gemini import ask_gemini, estimate_macros_with_gemini, analyze_meal_photo_with_gemini

PRO_PRICE = 9.99
FREE_CHATBOT_DAILY_LIMIT = 5
FREE_FOOD_SCAN_DAILY_LIMIT = 2


@login_required
def index(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # User's recent meals and workouts
    meals = Meal.objects.filter(user=request.user).order_by('-date')[:6]
    workouts = Workout.objects.filter(user=request.user).order_by('-date')[:6]
    payments = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')[:5]

    # Calculate statistics for Dashboard
    total_meals_count = Meal.objects.filter(user=request.user).count()
    total_workouts_count = Workout.objects.filter(user=request.user).count()
    
    # Calculate calories consumed today or total
    today = timezone.now().date()
    today_meals = Meal.objects.filter(user=request.user, date__date=today)
    today_calories = today_meals.aggregate(Sum('calories'))['calories__sum'] or 0
    
    # Recent Purchases / Activities for the bottom table matching the dark mauve UI
    recent_transactions = []
    for p in payments:
        recent_transactions.append({
            'name': p.plan_name,
            'user_name': request.user.username.title(),
            'id_code': f"#{p.transaction_id[:8].upper()}",
            'amount': f"${p.amount:.2f}",
            'status': 'Paid' if p.status == 'completed' else p.status.capitalize(),
            'type': 'pro_sub',
            'date': p.created_at,
            'is_paid': True
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
            'is_paid': False
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
            'is_paid': False
        })

    recent_transactions = sorted(recent_transactions, key=lambda x: x['date'], reverse=True)[:6]

    # Chart monthly activity sample
    chart_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    chart_values = [45, 60, 95, 50, 85, 40]

    context = {
        'profile': profile,
        'meals': meals,
        'workouts': workouts,
        'payments': payments,
        'today_calories': today_calories,
        'total_meals_count': total_meals_count,
        'total_workouts_count': total_workouts_count,
        'recent_transactions': recent_transactions,
        'chart_months': chart_months,
        'chart_values': chart_values,
        'current_date': timezone.now(),
    }
    return render(request, 'siisto/index.html', context)


@login_required
def chatbot(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    chat_history = ChatMessage.objects.filter(user=request.user).order_by('date')
    
    # Daily limit check for free users
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
        
        if user_message:
            # Free limit enforcement
            if is_limit_reached:
                if is_ajax:
                    return JsonResponse({
                        'status': 'limit_reached',
                        'message': 'Maanta xadkaaga bilaashka ah ayaad gaadhay (5 fariin). Upgrade Pro si aad u hesho jawaabo aan xad lahayn!',
                        'upgrade_url': '/upgrade-pro/'
                    })
                messages.warning(request, "Maanta xadkaaga bilaashka ah ayaad gaadhay. Upgrade Pro!")
                return redirect('chatbot')

            custom_prompt = (
                f"Waxaad tahay Siisto AI Fitness & Health Coach — aad u caqlibadan, xirfadleh, "
                f"oo ku hadla Af-Soomaali iyo English. "
                f"Magaca isticmaalaha: {request.user.username}. "
                f"Miisaankiisa hadda: {profile.miisaan_hadda or 'Lama oga'} kg. "
                f"Miisaanka yoolka: {profile.miisaanka_yoolka or 'Lama oga'} kg. "
                f"Dhererka: {profile.dhererka or 'Lama oga'} cm. Jinsiga: {profile.jinsiga or 'Lama oga'}. "
                f"Hadafka: {profile.hadafka or 'Lama oga'}. "
                f"Pro Status: {'VIP Pro Member - hel adeeg buuxa' if profile.has_active_pro else 'Free Member'}.\n"
                "Uga jawaab si cilmiyeysan, sharraxaad buuxda, jadwal, iyo talooyin xirfadleh. "
                "Isticmaal Arabic numbers, bullet points, iyo markdown. "
                "Haddii su'aashu ay tahay Soomaali, ka jawaab Soomaali. Haddii English, ka jawaab English."
            )
            
            ai_response = ask_gemini(user_message, custom_system_prompt=custom_prompt, is_pro=profile.has_active_pro)
            
            msg_obj = ChatMessage.objects.create(
                user=request.user,
                message=user_message,
                response=ai_response
            )
            
            # Update count for response
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


@login_required
def upgrade_pro(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    recent_payments = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'siisto/payment.html', {
        'profile': profile,
        'recent_payments': recent_payments,
        'price': PRO_PRICE,
    })


@login_required
def process_payment(request):
    if request.method == "POST":
        payment_method = request.POST.get('payment_method', 'EVC Plus')
        phone_number = request.POST.get('phone_number', '')
        plan_name = request.POST.get('plan_name', 'Siisto Pro Monthly')
        amount = PRO_PRICE
        
        tx_id = f"TX-{uuid.uuid4().hex[:10].upper()}"
        
        tx = PaymentTransaction.objects.create(
            user=request.user,
            plan_name=plan_name,
            amount=amount,
            currency='USD',
            payment_method=payment_method,
            phone_number=phone_number,
            transaction_id=tx_id,
            status='completed',
            expiry_date=timezone.now() + datetime.timedelta(days=30)
        )
        
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.is_pro = True
        profile.pro_expires_at = tx.expiry_date
        profile.save()
        
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true'
        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': f'Hambalyo! Waxaad si guul leh ugu biirtay {plan_name} (${PRO_PRICE:.2f}/bishii).',
                'tx_id': tx_id,
                'expires_at': profile.pro_expires_at.strftime('%d %b %Y')
            })
            
        messages.success(request, f"🎉 Hambalyo! Waxaad si guul leh ugu biirtay Pro Plan (${PRO_PRICE:.2f}/bishii). Transaction ID: {tx_id}")
        return redirect('index')
        
    return redirect('upgrade_pro')


@login_required
def add_meal(request):
    if request.method == "POST":
        name = request.POST.get('name') or "Healthy Meal"
        raw_calories = request.POST.get('calories')
        raw_protein = request.POST.get('protein')
        raw_carbs = request.POST.get('carbs')
        raw_fats = request.POST.get('fats')
        image = request.FILES.get('meal_image')

        cal_val = None
        prot_val = None
        carb_val = None
        fat_val = None

        if raw_calories and raw_calories.strip():
            try:
                cal_val = int(raw_calories)
            except ValueError:
                pass

        if raw_protein and raw_protein.strip():
            try:
                prot_val = float(raw_protein)
            except ValueError:
                pass

        if raw_carbs and raw_carbs.strip():
            try:
                carb_val = float(raw_carbs)
            except ValueError:
                pass

        if raw_fats and raw_fats.strip():
            try:
                fat_val = float(raw_fats)
            except ValueError:
                pass

        if cal_val is None and name:
            ai_macros = estimate_macros_with_gemini(name)
            cal_val = cal_val or ai_macros['calories']
            prot_val = prot_val if prot_val is not None else ai_macros['protein']
            carb_val = carb_val if carb_val is not None else ai_macros['carbs']
            fat_val = fat_val if fat_val is not None else ai_macros['fats']
        else:
            cal_val = cal_val or 450
            prot_val = prot_val if prot_val is not None else 25.0
            carb_val = carb_val if carb_val is not None else 45.0
            fat_val = fat_val if fat_val is not None else 12.0

        Meal.objects.create(
            user=request.user,
            name=name,
            calories=cal_val,
            protein=prot_val,
            carbs=carb_val,
            fats=fat_val,
            image=image
        )
        messages.success(request, f"Cuntada '{name}' si guul leh ayaa loo keydiyay! ({cal_val} kcal, {prot_val}g protein)")
        return redirect('add_meal')

    user_meals = Meal.objects.filter(user=request.user).order_by('-date')
    latest_meal = user_meals.first()
    return render(request, 'siisto/food.html', {'latest_meal': latest_meal, 'user_meals': user_meals})


@login_required
@require_POST
def api_analyze_meal_photo(request):
    """
    Receives an uploaded meal photo, uses Gemini AI Vision to estimate macros.
    Free users: 2 scans/day. Pro users: Unlimited.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # Daily scan limit for free users
    if not profile.has_active_pro:
        today = timezone.now().date()
        # Count today's meals that were created (as proxy for photo scans)
        today_meal_count = Meal.objects.filter(user=request.user, date__date=today).count()
        if today_meal_count >= FREE_FOOD_SCAN_DAILY_LIMIT:
            return JsonResponse({
                'status': 'limit_reached',
                'message': f'Maanta {FREE_FOOD_SCAN_DAILY_LIMIT} scan oo bilaash ah ayaad isticmaalatay. Upgrade Pro si aad u hesho scan aan xad lahayn!',
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
            'disclaimer': 'Qiyaastan waxaa soo saaray AI (Gemini Vision). Fadlan sax ama xaqiiji ka hor inta aadan keydin.'
        }
    })


@login_required
def edit_meal(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id, user=request.user)
    if request.method == "POST":
        name = request.POST.get('name')
        calories = request.POST.get('calories')
        protein = request.POST.get('protein')
        carbs = request.POST.get('carbs')
        fats = request.POST.get('fats')

        if name:
            meal.name = name
            meal.calories = int(calories) if calories else 0
            meal.protein = float(protein) if protein else 0.0
            meal.carbs = float(carbs) if carbs else 0.0
            meal.fats = float(fats) if fats else 0.0
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


@login_required
def add_workout(request):
    """
    Task 1 & 2: Lists categorized exercises from ExerciseLibrary and logs workouts.
    """
    exercises = ExerciseLibrary.objects.all().order_by('category', 'subcategory', 'name')
    if request.method == "POST":
        name = request.POST.get('name')
        duration = request.POST.get('duration')
        sets = request.POST.get('sets') or 4
        reps = request.POST.get('reps') or 10
        weight_kg = request.POST.get('weight_kg') or 0
        exercise_id = request.POST.get('exercise_id')
        
        exercise_obj = None
        if exercise_id:
            try:
                exercise_obj = ExerciseLibrary.objects.get(id=int(exercise_id))
            except (ExerciseLibrary.DoesNotExist, ValueError):
                pass

        if name and duration:
            Workout.objects.create(
                user=request.user, 
                name=name, 
                duration=int(duration),
                sets=int(sets),
                reps=int(reps),
                weight_kg=float(weight_kg),
                exercise=exercise_obj,
                video_3d_url=exercise_obj.video_3d_url if exercise_obj else None
            )
            messages.success(request, f"Jimicsiga '{name}' si guul leh ayaa loo diiwaangeliyay!")
            return redirect('index')

    return render(request, 'siisto/gym.html', {'exercises': exercises})


@login_required
@require_POST
def api_update_exercise_video(request, exercise_id):
    """
    Task 2: Updates the custom video link (Pinterest/YouTube/Direct link) for an exercise
    directly in the database so it persists across sessions and users.
    """
    exercise = get_object_or_404(ExerciseLibrary, id=exercise_id)
    try:
        data = json.loads(request.body)
        new_video_url = data.get('video_url', '').strip()
    except Exception:
        new_video_url = request.POST.get('video_url', '').strip()

    exercise.video_3d_url = new_video_url
    exercise.save(update_fields=['video_3d_url'])

    return JsonResponse({
        'status': 'success',
        'message': f"Video URL-ka jimicsiga '{exercise.name}' si toos ah ayaa database-ka loogu keydiyay!",
        'exercise_id': exercise.id,
        'video_url': exercise.video_3d_url
    })


@login_required
def ai_form_detection(request):
    """
    AI Exercise Form Detection with MediaPipe Pose Landmarker.
    Tracks all exercises in real-time: Squats, Push-ups, Bicep Curls,
    Shoulder Press, Lunges, Plank, Sit-ups.
    Free = Squats only. Pro = All exercises.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)
    locked_exercises = ['Push-Ups', 'Bicep Curls', 'Shoulder Press', 'Lunges', 'Plank', 'Sit-Ups']
    return render(request, 'siisto/ai_form_detection.html', {
        'profile': profile,
        'locked_exercises': locked_exercises,
    })


@login_required
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == "POST":
        name = request.POST.get('name')
        duration = request.POST.get('duration')
        
        if name and duration:
            workout.name = name
            workout.duration = int(duration)
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


@login_required
def history(request):
    meals = Meal.objects.filter(user=request.user).order_by('-date')
    workouts = Workout.objects.filter(user=request.user).order_by('-date')
    payments = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'siisto/history.html', {
        'cuntooyinka': meals, 
        'jimicsiyada': workouts,
        'payments': payments
    })


@login_required
def progress_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    total_meals = Meal.objects.filter(user=request.user).count()
    total_workouts = Workout.objects.filter(user=request.user).count()
    total_logs = total_meals + total_workouts
    target = 14
    percentage = min(int((total_logs / target) * 100), 100) if target > 0 else 0
    weight_logs = WeightLog.objects.filter(user=request.user).order_by('date')
    
    return render(request, 'siisto/progress.html', {
        'total_meals': total_meals,
        'total_workouts': total_workouts,
        'percentage': percentage,
        'profile': profile,
        'weight_logs': weight_logs
    })


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        if 'weight_submit' in request.POST:
            weight_val = request.POST.get('miisaanka')
            if weight_val:
                WeightLog.objects.create(user=request.user, weight=float(weight_val))
                messages.success(request, "Miisaanka maanta waa la keydiyay!")
        elif 'goal_submit' in request.POST:
            goal_val = request.POST.get('miisaanka_yoolka')
            if goal_val:
                profile.miisaanka_yoolka = float(goal_val)
                profile.save()
                messages.success(request, "Miisaanka yoolka waa la cusbooneysiiyay!")
        return redirect('profile')

    weight_logs = WeightLog.objects.filter(user=request.user).order_by('-date')
    payments = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'siisto/profile.html', {
        'profile': profile, 
        'weight_logs': weight_logs,
        'payments': payments
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, "Furaha sirta ah isma laha (Passwords do not match).")
        elif not username or not password:
            messages.error(request, "Fadlan buuxi dhammaan meelaha banaan.")
        else:
            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                messages.error(request, "Magacan horay ayaa loo qaatay. Fadlan mid kale dooro.")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                Profile.objects.create(user=user)
                login(request, user)
                messages.success(request, f"Ku soo dhowow Siisto Fitness Tracker, {user.username}!")
                return redirect('index')

    return render(request, 'registration/signup.html')


def onboarding_3d(request):
    """
    3D Interactive Scrolling Onboarding & Fitness Assessment Page.
    """
    profile = None
    initial_data = {
        'weight': 70.0,
        'height': 175.0,
        'age': 25,
        'gender': 'male',
        'goal': 'lose_weight',
        'activity_level': 'moderate',
        'target_weight': 65.0,
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
    })


@require_POST
def api_save_onboarding(request):
    """
    API endpoint to calculate fitness diagnostics and save onboarding responses.
    """
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

        # 1. BMI Calculation
        height_m = max(height / 100.0, 0.5)
        bmi = round(weight / (height_m * height_m), 1)
        if bmi < 18.5:
            bmi_status = "Miisaan Hooseeya (Underweight)"
            bmi_color = "#38bdf8"
        elif bmi < 25.0:
            bmi_status = "Miisaan Caafimaad Leh (Healthy / Normal)"
            bmi_color = "#4ade80"
        elif bmi < 30.0:
            bmi_status = "Miisaan Zaa'id ah (Overweight)"
            bmi_color = "#fbbf24"
        else:
            bmi_status = "Buran / Cayil Sare (Obese)"
            bmi_color = "#f87171"

        # 2. BMR (Mifflin-St Jeor)
        if gender == 'female':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        bmr = round(bmr, 0)

        # 3. TDEE based on activity
        activity_multipliers = {
            'sedentary': 1.2,
            'moderate': 1.45,
            'active': 1.725,
            'very_active': 1.9
        }
        mult = activity_multipliers.get(activity_level, 1.45)
        tdee = round(bmr * mult, 0)

        # 4. Target Calories according to Goal
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
            goal_label = "Jir Dhis & Awood (Fitness & Stamina)"
        else:
            target_calories = int(tdee)
            protein_factor = 1.6
            goal_label = "Caafimaad Guud & Joogteyn (Longevity)"

        # 5. Hydration & Macronutrients
        water_liters = round(weight * 0.035, 1)
        protein_g = int(weight * protein_factor)
        fats_g = int((target_calories * 0.25) / 9)
        carbs_g = max(int((target_calories - (protein_g * 4 + fats_g * 9)) / 4), 50)

        # 6. Timeline estimate (safe ~0.5kg/week change)
        diff = abs(weight - target_weight)
        estimated_weeks = max(int(diff / 0.5), 1) if diff > 0.5 else 4

        # Persist if logged in
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
            profile.save()

            # Record initial WeightLog
            WeightLog.objects.create(user=request.user, weight=weight)

        return JsonResponse({
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
                'target_weight': target_weight
            },
            'redirect_url': '/progress/' if request.user.is_authenticated else '/signup/'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@staff_member_required
def admin_dashboard(request):
    """
    Custom Admin Dashboard with rich stats and user management.
    """
    total_users = User.objects.count()
    pro_users = Profile.objects.filter(is_pro=True).count()
    free_users = total_users - pro_users
    total_meals = Meal.objects.count()
    total_workouts = Workout.objects.count()
    total_revenue = PaymentTransaction.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    total_transactions = PaymentTransaction.objects.filter(status='completed').count()
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_payments = PaymentTransaction.objects.select_related('user').order_by('-created_at')[:10]
    recent_meals = Meal.objects.select_related('user').order_by('-date')[:8]
    recent_workouts = Workout.objects.select_related('user').order_by('-date')[:8]
    
    # Monthly revenue (last 6 months)
    from django.db.models.functions import TruncMonth
    monthly_revenue = (
        PaymentTransaction.objects
        .filter(status='completed')
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-month')[:6]
    )
    
    return render(request, 'siisto/admin_dashboard.html', {
        'total_users': total_users,
        'pro_users': pro_users,
        'free_users': free_users,
        'total_meals': total_meals,
        'total_workouts': total_workouts,
        'total_revenue': total_revenue,
        'total_transactions': total_transactions,
        'recent_users': recent_users,
        'recent_payments': recent_payments,
        'recent_meals': recent_meals,
        'recent_workouts': recent_workouts,
        'monthly_revenue': list(monthly_revenue),
    })