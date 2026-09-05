import json
from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

from .models import (
    Profile, Meal, Workout, ExerciseLibrary,
    WeightLog, Routine90, PaymentTransaction, Notification, ChatMessage
)
from .context_processors import siisto_i18n
from .templatetags.siisto_tags import ui_trans
from .gemini import ask_gemini, get_smart_multilingual_fitness_response


class SiistoComprehensiveTestSuite(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        # Primary user
        self.user1 = User.objects.create_user(
            username='athlete_one',
            email='athlete1@siisto.com',
            password='TestPassword123!',
            first_name='Cabdi'
        )
        self.profile1 = Profile.objects.create(
            user=self.user1,
            dhererka=178.0,
            da_da=24,
            jinsiga='male',
            hadafka='build_muscle',
            heerka_dhaqdhaqaaqa='active',
            miisaanka_yoolka=75.0,
            fitness_level='intermediate',
            preferred_language='so',
            is_pro=False
        )

        # Secondary user (for data isolation checks)
        self.user2 = User.objects.create_user(
            username='athlete_two',
            email='athlete2@siisto.com',
            password='TestPassword123!',
            first_name='Faarax'
        )
        self.profile2 = Profile.objects.create(
            user=self.user2,
            dhererka=170.0,
            da_da=28,
            jinsiga='male',
            hadafka='lose_weight',
            heerka_dhaqdhaqaaqa='moderate',
            miisaanka_yoolka=65.0,
            preferred_language='en',
            is_pro=False
        )

        # Staff user
        self.staff_user = User.objects.create_user(
            username='admin_test',
            email='admin@siisto.com',
            password='TestPassword123!',
            is_staff=True
        )

        # Sample Exercises for each target category
        self.squat = ExerciseLibrary.objects.create(
            name='Barbell Squat',
            category='Legs',
            subcategory='Quadriceps',
            target_muscle='Quadriceps / Glutes',
            difficulty='intermediate',
            description='Compound lower-body squat movement.',
            correct_form_instructions='Keep knees aligned with toes, hips back, reach 90 degree depth.',
            default_sets=4,
            default_reps=10,
            default_duration=20
        )
        self.bench_press = ExerciseLibrary.objects.create(
            name='Bench Press',
            category='Chest',
            subcategory='Pectorals',
            target_muscle='Pectoralis Major',
            difficulty='intermediate',
            description='Compound chest press.',
            correct_form_instructions='Elbows at 45-70 degrees, press up smoothly.',
            default_sets=4,
            default_reps=8,
            default_duration=15
        )
        self.bicep_curl = ExerciseLibrary.objects.create(
            name='Dumbbell Bicep Curl',
            category='Arms',
            subcategory='Biceps',
            target_muscle='Biceps Brachii',
            difficulty='beginner',
            description='Isolation arm flexion.',
            correct_form_instructions='Keep elbows pinned to your sides, squeeze at the peak.',
            default_sets=3,
            default_reps=12,
            default_duration=10
        )
        self.shoulder_press = ExerciseLibrary.objects.create(
            name='Overhead Shoulder Press',
            category='Shoulders',
            subcategory='Deltoids',
            target_muscle='Anterior Deltoid',
            difficulty='intermediate',
            description='Vertical overhead pressing.',
            correct_form_instructions='Full overhead extension with stable core.',
            default_sets=4,
            default_reps=10,
            default_duration=15
        )
        self.crunch = ExerciseLibrary.objects.create(
            name='Abdominal Crunches',
            category='Abs / Core',
            subcategory='Abdominals',
            target_muscle='Rectus Abdominis',
            difficulty='beginner',
            description='Core flexion movement.',
            correct_form_instructions='Engage abdominals, do not strain neck.',
            default_sets=3,
            default_reps=20,
            default_duration=10
        )

    # ─────────────────────────────────────────────────────
    #  1. AUTHENTICATION & PROFILE TESTS
    # ─────────────────────────────────────────────────────

    def test_signup(self):
        """Test new user registration."""
        response = self.client.post(reverse('signup'), {
            'username': 'new_athlete',
            'email': 'new@siisto.com',
            'first_name': 'NewUser',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.filter(username='new_athlete').first()
        self.assertIsNotNone(new_user)
        self.assertTrue(Profile.objects.filter(user=new_user).exists())

    def test_profile_update_and_language_persistence(self):
        """Test updating profile biometrics and preferred language."""
        self.client.login(username='athlete_one', password='TestPassword123!')
        response = self.client.post(reverse('profile'), {
            'action': 'profile',
            'dhererka': 180.5,
            'da_da': 25,
            'jinsiga': 'male',
            'hadafka': 'build_muscle',
            'heerka_dhaqdhaqaaqa': 'very_active',
            'miisaanka_yoolka': 80.0,
            'preferred_language': 'ar',
            'email': 'updated@siisto.com',
        })
        self.assertEqual(response.status_code, 302)
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.dhererka, 180.5)
        self.assertEqual(self.profile1.preferred_language, 'ar')
        self.assertEqual(self.profile1.language, 'ar')

    # ─────────────────────────────────────────────────────
    #  2. MULTILINGUAL & RTL TESTS (Somali, English, Arabic)
    # ─────────────────────────────────────────────────────

    def test_set_language_preference_route(self):
        """Test switching language to Arabic, English, and Somali."""
        self.client.login(username='athlete_one', password='TestPassword123!')

        # Switch to Arabic
        res_ar = self.client.post(reverse('set_language_preference'), {'language': 'ar', 'next': '/'})
        self.assertEqual(res_ar.status_code, 302)
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.preferred_language, 'ar')
        self.assertEqual(self.client.cookies.get(settings.LANGUAGE_COOKIE_NAME).value, 'ar')

        # Switch to English
        res_en = self.client.post(reverse('set_language_preference'), {'language': 'en', 'next': '/'})
        self.assertEqual(res_en.status_code, 302)
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.preferred_language, 'en')

        # Switch to Somali
        res_so = self.client.post(reverse('set_language_preference'), {'language': 'so', 'next': '/'})
        self.assertEqual(res_so.status_code, 302)
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.preferred_language, 'so')

    def test_context_processor_rtl_for_arabic(self):
        """Test context processor supplies dir='rtl' and IS_RTL=True for Arabic."""
        req_ar = self.factory.get('/')
        req_ar.user = self.user1
        self.profile1.preferred_language = 'ar'
        self.profile1.save()

        ctx_ar = siisto_i18n(req_ar)
        self.assertEqual(ctx_ar['CURRENT_LANGUAGE'], 'ar')
        self.assertEqual(ctx_ar['ACTIVE_LANG_DIR'], 'rtl')
        self.assertTrue(ctx_ar['IS_RTL'])

        # English -> ltr
        req_en = self.factory.get('/')
        req_en.user = self.user2
        ctx_en = siisto_i18n(req_en)
        self.assertEqual(ctx_en['CURRENT_LANGUAGE'], 'en')
        self.assertEqual(ctx_en['ACTIVE_LANG_DIR'], 'ltr')
        self.assertFalse(ctx_en['IS_RTL'])

    def test_ui_trans_filter(self):
        """Test ui_trans template filter returns correct translations."""
        # Somali
        self.assertEqual(ui_trans("Dashboard", "so"), "Kala-bixidda Guud (Dashboard)")
        self.assertEqual(ui_trans("AI Coach", "so"), "Macallinka AI (AI Coach)")
        # English
        self.assertEqual(ui_trans("Dashboard", "en"), "Dashboard")
        self.assertEqual(ui_trans("AI Coach", "en"), "AI Coach")
        # Arabic
        self.assertEqual(ui_trans("Dashboard", "ar"), "لوحة التحكم (Dashboard)")
        self.assertEqual(ui_trans("AI Coach", "ar"), "مدرب الذكاء الاصطناعي")

    # ─────────────────────────────────────────────────────
    #  3. EXERCISE TARGET MAPPING & AI FORM DETECTION TESTS
    # ─────────────────────────────────────────────────────

    def test_exercise_target_mappings(self):
        """
        Verify required mappings:
        - Squat: Category = Legs, Target = Quads / Glutes
        - Bench Press: Category = Chest, Target = Chest
        - Bicep Curl: Category = Arms, Target = Biceps
        - Shoulder Press: Category = Shoulders, Target = Shoulders
        - Crunch: Category = Abs / Core, Target = Abdominals
        """
        self.assertEqual(self.squat.category, 'Legs')
        self.assertIn('Quadriceps', self.squat.target_muscle)

        self.assertEqual(self.bench_press.category, 'Chest')
        self.assertIn('Pectoral', self.bench_press.target_muscle)

        self.assertEqual(self.bicep_curl.category, 'Arms')
        self.assertIn('Biceps', self.bicep_curl.target_muscle)

        self.assertEqual(self.shoulder_press.category, 'Shoulders')
        self.assertIn('Deltoid', self.shoulder_press.target_muscle)

        self.assertEqual(self.crunch.category, 'Abs / Core')
        self.assertIn('Abdomin', self.crunch.target_muscle)

    def test_ai_form_detection_view_renders(self):
        """Test that ai_form_detection view loads successfully with categories."""
        self.client.login(username='athlete_one', password='TestPassword123!')
        response = self.client.get(reverse('ai_form_detection'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Real-Time Exercise Form')
        self.assertContains(response, 'Squats')
        self.assertContains(response, 'Bench Press')

    # ─────────────────────────────────────────────────────
    #  4. AI CHATBOT CONTEXT & MULTILINGUAL TESTS
    # ─────────────────────────────────────────────────────

    def test_gemini_fallback_context_awareness(self):
        """Test fallback engine responds accurately to multi-turn context (e.g. chest sets, 60kg meals)."""
        # Follow-up query about sets when previous context was chest
        resp_sets = get_smart_multilingual_fitness_response(
            "how many sets?",
            is_pro=True,
            language='en',
            history="User: I want chest exercises\nAI: Barbell bench press and incline press are great."
        )
        self.assertIn("Chest", resp_sets)
        self.assertIn("sets", resp_sets.lower())

        # Somali meal query with 60kg context
        resp_meal_so = get_smart_multilingual_fitness_response("cunto noocee ah ayaan cunaa?", language='so')
        self.assertIn("Borotiin", resp_meal_so)

        # Arabic chest query
        resp_chest_ar = get_smart_multilingual_fitness_response("ما هي تمارين الصدر؟", language='ar')
        self.assertIn("الصدر", resp_chest_ar)

    @patch('siisto.views.ask_gemini', return_value="Great AI Coach Response")
    def test_chatbot_view_creates_message_and_enforces_limit(self, mock_gemini):
        """Test chatbot creates ChatMessage and enforces free tier limit (5 messages)."""
        self.client.login(username='athlete_one', password='TestPassword123!')

        # Send 5 messages
        for i in range(5):
            res = self.client.post(
                reverse('chatbot'),
                {'user_message': f'Message number {i+1}'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.content)
            self.assertEqual(data['status'], 'success')

        self.assertEqual(ChatMessage.objects.filter(user=self.user1).count(), 5)

        # 6th message should hit limit
        res_limit = self.client.post(
            reverse('chatbot'),
            {'user_message': 'Message number 6'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(res_limit.status_code, 200)
        data_limit = json.loads(res_limit.content)
        self.assertEqual(data_limit['status'], 'limit_reached')

    # ─────────────────────────────────────────────────────
    #  5. AI RECOMMENDATIONS TESTS
    # ─────────────────────────────────────────────────────

    @patch('siisto.views.ask_gemini', return_value="Personalized 7-Day Workout Routine")
    def test_workout_recommendation_view(self, mock_gemini):
        """Test workout recommendation view loads with personalized prompt."""
        self.client.login(username='athlete_one', password='TestPassword123!')
        response = self.client.get(reverse('workout_recommendation'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Workout Plan')

    @patch('siisto.views.ask_gemini', return_value="Personalized 7-Day Nutrition Plan")
    def test_meal_recommendation_view(self, mock_gemini):
        """Test meal recommendation view loads with nutrition breakdown."""
        self.client.login(username='athlete_one', password='TestPassword123!')
        response = self.client.get(reverse('meal_recommendation'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Meal Plan')

    # ─────────────────────────────────────────────────────
    #  6. 3D EXERCISE VIDEOS & ADMIN CONTROLS
    # ─────────────────────────────────────────────────────

    def test_admin_update_exercise_video_api(self):
        """Test staff can update and delete exercise video URL."""
        self.client.login(username='admin_test', password='TestPassword123!')

        # Update video URL
        res = self.client.post(
            reverse('api_update_exercise_video', args=[self.squat.id]),
            data=json.dumps({'video_url': 'https://www.youtube.com/watch?v=aclHkVaku9U'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.squat.refresh_from_db()
        self.assertEqual(self.squat.video_3d_url, 'https://www.youtube.com/watch?v=aclHkVaku9U')

        # Delete video
        res_del = self.client.post(
            reverse('api_update_exercise_video', args=[self.squat.id]),
            data={'action': 'delete'}
        )
        self.assertEqual(res_del.status_code, 200)
        self.squat.refresh_from_db()
        self.assertEqual(self.squat.video_3d_url, '')

    # ─────────────────────────────────────────────────────
    #  7. 90-DAY CHALLENGE & TRACKING
    # ─────────────────────────────────────────────────────

    def test_90_day_challenge_start_and_complete_day(self):
        """Test starting challenge and completing days with streak tracking."""
        self.client.login(username='athlete_one', password='TestPassword123!')

        # Start challenge
        res_start = self.client.post(reverse('challenge_90day'), {'action': 'start'})
        self.assertEqual(res_start.status_code, 302)
        challenge = Routine90.objects.filter(user=self.user1, is_active=True).first()
        self.assertIsNotNone(challenge)
        self.assertEqual(challenge.current_day, 1)

        # Complete Day 1
        res_comp = self.client.post(reverse('challenge_90day'), {'action': 'complete_day'})
        self.assertEqual(res_comp.status_code, 302)
        challenge.refresh_from_db()
        self.assertEqual(challenge.current_day, 2)
        self.assertEqual(challenge.streak, 1)

    # ─────────────────────────────────────────────────────
    #  8. PAYPAL PAYMENT & SERVER-SIDE PRO ACTIVATION
    # ─────────────────────────────────────────────────────

    def test_pro_activation_and_expiration(self):
        """Test profile has_active_pro server-side expiration validation."""
        self.assertFalse(self.profile1.has_active_pro)

        # Set pro active with future date
        self.profile1.is_pro = True
        self.profile1.pro_expires_at = timezone.now() + timedelta(days=30)
        self.profile1.save()
        self.assertTrue(self.profile1.has_active_pro)

        # Expired pro
        self.profile1.pro_expires_at = timezone.now() - timedelta(days=1)
        self.profile1.save()
        self.assertFalse(self.profile1.has_active_pro)

    def test_paypal_webhook_rejects_missing_headers_or_signature(self):
        """Unverified webhook calls without valid PayPal signature headers must be rejected."""
        event_payload = {
            'event_type': 'PAYMENT.CAPTURE.COMPLETED',
            'resource': {
                'id': 'CAP-FORGED-12345',
                'amount': {'value': '9.99'}
            }
        }
        # Post with no signature headers
        response = self.client.post(
            reverse('paypal_webhook'),
            data=json.dumps(event_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data.get('status'), 'error')
        self.assertIn('signature verification failed', data.get('message', ''))

    @patch('siisto.views.requests.post')
    @patch('siisto.views.get_paypal_access_token')
    def test_paypal_webhook_verified_activates_pro(self, mock_get_token, mock_post):
        """Verified PayPal webhook activates user Pro membership correctly."""
        mock_get_token.return_value = 'mock-access-token-123'

        # Mock verify-webhook-signature API response
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'verification_status': 'SUCCESS'}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        # Create pending transaction
        tx = PaymentTransaction.objects.create(
            user=self.user1,
            plan_name='Siisto Pro Monthly',
            plan_type='monthly',
            amount=9.99,
            currency='USD',
            payment_method='paypal',
            transaction_id='TX-TEST-VERIFY-001',
            paypal_order_id='ORD-TEST-001',
            paypal_capture_id='CAP-REAL-123',
            status='pending',
        )

        event_payload = {
            'event_type': 'PAYMENT.CAPTURE.COMPLETED',
            'resource': {
                'id': 'CAP-REAL-123',
                'amount': {'value': '9.99'}
            }
        }

        with self.settings(PAYPAL_WEBHOOK_ID='WH-TEST-VALID-ID'):
            response = self.client.post(
                reverse('paypal_webhook'),
                data=json.dumps(event_payload),
                content_type='application/json',
                HTTP_PAYPAL_AUTH_ALGO='SHA256withRSA',
                HTTP_PAYPAL_CERT_URL='https://api.sandbox.paypal.com/v1/notifications/certs/CERT-123',
                HTTP_PAYPAL_TRANSMISSION_ID='tx-uuid-1234',
                HTTP_PAYPAL_TRANSMISSION_SIG='base64-sig-string',
                HTTP_PAYPAL_TRANSMISSION_TIME='2026-09-05T12:00:00Z',
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 'ok')

        tx.refresh_from_db()
        self.assertEqual(tx.status, 'completed')
        self.assertEqual(tx.paypal_webhook_event, 'PAYMENT.CAPTURE.COMPLETED')

        self.profile1.refresh_from_db()
        self.assertTrue(self.profile1.is_pro)
        self.assertTrue(self.profile1.has_active_pro)

    @patch('siisto.views.requests.post')
    @patch('siisto.views.get_paypal_access_token')
    def test_paypal_webhook_rejects_failed_signature(self, mock_get_token, mock_post):
        """If PayPal API verification returns FAILURE, reject with 400."""
        mock_get_token.return_value = 'mock-access-token-123'

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'verification_status': 'FAILURE'}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        event_payload = {
            'event_type': 'PAYMENT.CAPTURE.COMPLETED',
            'resource': {
                'id': 'CAP-FORGED-999',
                'amount': {'value': '9.99'}
            }
        }

        with self.settings(PAYPAL_WEBHOOK_ID='WH-TEST-VALID-ID'):
            response = self.client.post(
                reverse('paypal_webhook'),
                data=json.dumps(event_payload),
                content_type='application/json',
                HTTP_PAYPAL_AUTH_ALGO='SHA256withRSA',
                HTTP_PAYPAL_CERT_URL='https://api.sandbox.paypal.com/v1/notifications/certs/CERT-123',
                HTTP_PAYPAL_TRANSMISSION_ID='tx-uuid-1234',
                HTTP_PAYPAL_TRANSMISSION_SIG='invalid-sig',
                HTTP_PAYPAL_TRANSMISSION_TIME='2026-09-05T12:00:00Z',
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('status'), 'error')

    # ─────────────────────────────────────────────────────
    #  9. USER DATA ISOLATION
    # ─────────────────────────────────────────────────────

    def test_user_data_isolation(self):
        """Ensure meals, workouts, weight logs belong strictly to authenticated user."""
        Meal.objects.create(user=self.user1, name='User1 Oats', calories=400, protein=20, carbs=50, fats=5)
        Meal.objects.create(user=self.user2, name='User2 Rice', calories=600, protein=30, carbs=80, fats=10)

        Workout.objects.create(user=self.user1, name='User1 Squat', body_part='Legs', sets=4, reps=10, duration=30)
        Workout.objects.create(user=self.user2, name='User2 Bench', body_part='Chest', sets=4, reps=8, duration=25)

        self.client.login(username='athlete_one', password='TestPassword123!')

        history_res = self.client.get(reverse('history'))
        self.assertEqual(history_res.status_code, 200)
        self.assertContains(history_res, 'User1 Oats')
        self.assertNotContains(history_res, 'User2 Rice')
        self.assertContains(history_res, 'User1 Squat')
        self.assertNotContains(history_res, 'User2 Bench')
