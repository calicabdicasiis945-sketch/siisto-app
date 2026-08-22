from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('signup/', views.register, name='signup'),
    
    # Nutrition / Meals
    path('add-meal/', views.add_meal, name='add_meal'),
    path('food/', views.add_meal, name='food'),
    path('edit-meal/<int:meal_id>/', views.edit_meal, name='edit_meal'),
    path('delete-meal/<int:meal_id>/', views.delete_meal, name='delete_meal'),
    path('api/analyze-meal-photo/', views.api_analyze_meal_photo, name='api_analyze_meal_photo'),
    
    # Workouts & Gym
    path('add-workout/', views.add_workout, name='add_workout'),
    path('gym/', views.add_workout, name='gym'),
    path('edit-workout/<int:workout_id>/', views.edit_workout, name='edit_workout'),
    path('delete-workout/<int:workout_id>/', views.delete_workout, name='delete_workout'),
    path('api/exercise/<int:exercise_id>/update-video/', views.api_update_exercise_video, name='api_update_exercise_video'),
    
    # AI Exercise Form Detection (MediaPipe Pose Landmarker)
    path('ai-form-detection/', views.ai_form_detection, name='ai_form_detection'),

    # AI Coach / Chatbot (Single consolidated instance)
    path('ai-coach/', views.chatbot, name='ai_coach'),
    path('chatbot/', views.chatbot, name='chatbot'),
    
    # Tracking & Profile
    path('history/', views.history, name='history'),
    path('progress/', views.progress_view, name='progress'),
    path('profile/', views.profile_view, name='profile'),
    
    # 3D Scrolling Interactive Onboarding & Body Scan
    path('onboarding/', views.onboarding_3d, name='onboarding_3d'),
    path('api/save-onboarding/', views.api_save_onboarding, name='api_save_onboarding'),
    
    # Pro Upgrade & Payment System ($9.99/month)
    path('upgrade-pro/', views.upgrade_pro, name='upgrade_pro'),
    path('process-payment/', views.process_payment, name='process_payment'),

    # Custom Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]