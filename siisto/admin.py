from django.contrib import admin
from .models import Profile, WeightLog, Meal, Workout, ChatMessage, Routine90, ExerciseLibrary, PaymentTransaction

@admin.register(ExerciseLibrary)
class ExerciseLibraryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'subcategory', 'target_muscle', 'video_3d_url', 'default_duration', 'default_sets', 'default_reps')
    list_filter = ('category', 'subcategory')
    search_fields = ('name', 'category', 'subcategory', 'target_muscle', 'description')
    list_editable = ('video_3d_url',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'subcategory', 'target_muscle', 'description')
        }),
        ('Media & Demonstration', {
            'fields': ('image_url', 'video_3d_url'),
            'description': 'Paste any Pinterest pin URL, YouTube embed, or hosted MP4 video link here.'
        }),
        ('Form & Execution', {
            'fields': ('correct_form_instructions', 'default_duration', 'default_sets', 'default_reps')
        }),
    )

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'calories', 'protein', 'carbs', 'fats', 'date')
    list_filter = ('date', 'user')
    search_fields = ('name', 'user__username')

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'duration', 'sets', 'reps', 'weight_kg', 'date')
    list_filter = ('date', 'user')
    search_fields = ('name', 'user__username')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_pro', 'pro_expires_at', 'miisaanka_yoolka')
    list_filter = ('is_pro',)
    search_fields = ('user__username', 'location')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_name', 'amount', 'currency', 'payment_method', 'transaction_id', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'transaction_id', 'phone_number')

admin.site.register(WeightLog)
admin.site.register(ChatMessage)
admin.site.register(Routine90)