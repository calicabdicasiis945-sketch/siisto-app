from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ─── Core / Dashboard ───────────────────────────────
    path('', views.index, name='index'),

    # ─── Auth ───────────────────────────────────────────
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.register, name='signup'),

    # ─── Nutrition / Meals ──────────────────────────────
    path('food/', views.add_meal, name='food'),
    path('add-meal/', views.add_meal, name='add_meal'),
    path('edit-meal/<int:meal_id>/', views.edit_meal, name='edit_meal'),
    path('delete-meal/<int:meal_id>/', views.delete_meal, name='delete_meal'),
    path('api/analyze-meal-photo/', views.api_analyze_meal_photo, name='api_analyze_meal_photo'),

    # ─── Workouts & Gym ─────────────────────────────────
    path('gym/', views.add_workout, name='gym'),
    path('add-workout/', views.add_workout, name='add_workout'),
    path('edit-workout/<int:workout_id>/', views.edit_workout, name='edit_workout'),
    path('delete-workout/<int:workout_id>/', views.delete_workout, name='delete_workout'),
    path('exercise/<int:exercise_id>/', views.exercise_detail, name='exercise_detail'),
    path('api/exercise/<int:exercise_id>/update-video/', views.api_update_exercise_video, name='api_update_exercise_video'),

    # ─── AI Features ────────────────────────────────────
    path('ai-coach/', views.chatbot, name='ai_coach'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('ai-form-detection/', views.ai_form_detection, name='ai_form_detection'),
    path('ai-recommendation/', views.ai_recommendation, name='ai_recommendation'),
    path('workout-recommendation/', views.workout_recommendation, name='workout_recommendation'),
    path('meal-recommendation/', views.meal_recommendation, name='meal_recommendation'),

    # ─── Tracking & Profile ─────────────────────────────
    path('history/', views.history, name='history'),
    path('progress/', views.progress_view, name='progress'),
    path('profile/', views.profile_view, name='profile'),

    # ─── 90-Day Challenge ───────────────────────────────
    path('90-day-challenge/', views.challenge_90day, name='challenge_90day'),
    path('api/complete-day/', views.api_complete_challenge_day, name='api_complete_challenge_day'),

    # ─── Onboarding ─────────────────────────────────────
    path('onboarding/', views.onboarding_3d, name='onboarding_3d'),
    path('api/save-onboarding/', views.api_save_onboarding, name='api_save_onboarding'),

    # ─── Pro Upgrade & PayPal Payment ───────────────────
    path('upgrade-pro/', views.upgrade_pro, name='upgrade_pro'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('paypal/create-order/', views.paypal_create_order, name='paypal_create_order'),
    path('paypal/capture-order/<str:order_id>/', views.paypal_capture_order, name='paypal_capture_order'),
    path('paypal/webhook/', views.paypal_webhook, name='paypal_webhook'),

    # ─── Notifications ──────────────────────────────────
    path('api/notifications/', views.api_get_notifications, name='api_get_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.api_mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/read-all/', views.api_mark_all_notifications_read, name='api_mark_all_notifications_read'),

    # ─── Language Switching ─────────────────────────────
    path('set-language/', views.set_language_preference, name='set_language_preference'),
    path('set-language/<str:lang_code>/', views.set_language_preference, name='set_language_preference_code'),

    # ─── Admin Dashboard ────────────────────────────────
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]