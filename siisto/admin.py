from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Profile, WeightLog, Meal, Workout, ChatMessage,
    Routine90, ExerciseLibrary, PaymentTransaction, Notification
)

admin.site.site_header = "Siisto Fitness Admin"
admin.site.site_title = "Siisto Admin"
admin.site.index_title = "Siisto Fitness Management"


# ─────────────────────────────────────────
#  EXERCISE LIBRARY
# ─────────────────────────────────────────
@admin.register(ExerciseLibrary)
class ExerciseLibraryAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'subcategory', 'difficulty',
        'target_muscle', 'has_video', 'has_image',
        'default_sets', 'default_reps', 'default_duration'
    )
    list_filter = ('category', 'subcategory', 'difficulty')
    search_fields = ('name', 'category', 'subcategory', 'target_muscle', 'description')
    ordering = ('category', 'subcategory', 'name')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'subcategory', 'target_muscle', 'difficulty', 'description')
        }),
        ('Form & Instructions', {
            'fields': ('correct_form_instructions',),
            'classes': ('collapse',),
        }),
        ('📹 Local Video Upload (Preferred)', {
            'fields': ('video_file',),
            'description': (
                'Upload the exercise 3D demonstration MP4 video here. '
                'This will be displayed in an HTML5 video player on the exercise page. '
                'Supported formats: MP4. Max size: 500MB.'
            ),
        }),
        ('🖼️ Exercise Image Upload', {
            'fields': ('image',),
            'description': 'Upload an exercise demonstration image (JPG/PNG/WebP).',
        }),
        ('🔗 Legacy URL Fields (Optional)', {
            'fields': ('image_url', 'video_3d_url'),
            'classes': ('collapse',),
            'description': 'These URL fields are kept for backwards compatibility. Local file uploads above take priority.',
        }),
        ('Default Workout Values', {
            'fields': ('default_duration', 'default_sets', 'default_reps'),
        }),
    )

    def has_video(self, obj):
        if obj.video_file:
            return format_html('<span style="color:green;">✅ Local File</span>')
        elif obj.video_3d_url:
            return format_html('<span style="color:orange;">🔗 URL</span>')
        return format_html('<span style="color:red;">❌ None</span>')
    has_video.short_description = 'Video'

    def has_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="40" style="border-radius:4px;" />', obj.image.url)
        elif obj.image_url:
            return format_html('<img src="{}" height="40" style="border-radius:4px;" />', obj.image_url)
        return '—'
    has_image.short_description = 'Image'


# ─────────────────────────────────────────
#  MEAL
# ─────────────────────────────────────────
@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'meal_type', 'calories', 'protein', 'carbs', 'fats', 'date')
    list_filter = ('meal_type', 'date', 'user')
    search_fields = ('name', 'user__username')
    date_hierarchy = 'date'
    readonly_fields = ('date',)


# ─────────────────────────────────────────
#  WORKOUT
# ─────────────────────────────────────────
@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'body_part', 'duration', 'sets', 'reps', 'weight_kg', 'date')
    list_filter = ('body_part', 'date', 'user')
    search_fields = ('name', 'user__username', 'body_part', 'notes')
    date_hierarchy = 'date'
    readonly_fields = ('date',)


# ─────────────────────────────────────────
#  PROFILE
# ─────────────────────────────────────────
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'is_pro', 'pro_status_display',
        'pro_expires_at', 'fitness_level', 'onboarding_completed'
    )
    list_filter = ('is_pro', 'fitness_level', 'jinsiga', 'onboarding_completed')
    search_fields = ('user__username', 'user__email', 'location')
    readonly_fields = ('miisaan_hadda', 'has_active_pro')
    actions = ['activate_pro', 'deactivate_pro']

    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal Info', {
            'fields': ('bio', 'location', 'birth_date', 'da_da', 'jinsiga')
        }),
        ('Fitness Data', {
            'fields': ('dhererka', 'miisaanka_yoolka', 'hadafka',
                       'heerka_dhaqdhaqaaqa', 'fitness_level', 'experience_level')
        }),
        ('Current Stats (Read-only)', {
            'fields': ('miisaan_hadda', 'has_active_pro'),
        }),
        ('Pro Membership', {
            'fields': ('is_pro', 'pro_started_at', 'pro_expires_at')
        }),
        ('Onboarding', {
            'fields': ('onboarding_completed',)
        }),
    )

    def pro_status_display(self, obj):
        if obj.has_active_pro:
            return format_html('<span style="color:green;font-weight:bold;">✅ Active Pro</span>')
        elif obj.is_pro:
            return format_html('<span style="color:red;">⚠️ Expired</span>')
        return format_html('<span style="color:gray;">Free</span>')
    pro_status_display.short_description = 'Pro Status'

    def activate_pro(self, request, queryset):
        import datetime
        for profile in queryset:
            profile.is_pro = True
            profile.pro_started_at = timezone.now()
            profile.pro_expires_at = timezone.now() + datetime.timedelta(days=30)
            profile.save()
        self.message_user(request, f"Activated Pro for {queryset.count()} users.")
    activate_pro.short_description = "✅ Activate Pro (30 days)"

    def deactivate_pro(self, request, queryset):
        queryset.update(is_pro=False, pro_expires_at=None)
        self.message_user(request, f"Deactivated Pro for {queryset.count()} users.")
    deactivate_pro.short_description = "❌ Deactivate Pro"


# ─────────────────────────────────────────
#  PAYMENT TRANSACTION
# ─────────────────────────────────────────
@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'plan_name', 'amount', 'currency',
        'payment_method', 'status_badge', 'transaction_id',
        'paypal_order_id', 'created_at'
    )
    list_filter = ('status', 'payment_method', 'plan_type', 'created_at')
    search_fields = ('user__username', 'transaction_id', 'paypal_order_id', 'paypal_capture_id')
    readonly_fields = ('created_at', 'updated_at', 'transaction_id')
    actions = ['mark_completed_activate_pro', 'mark_failed', 'mark_cancelled']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Transaction', {
            'fields': ('user', 'transaction_id', 'plan_name', 'plan_type', 'amount', 'currency', 'status')
        }),
        ('Payment Method', {
            'fields': ('payment_method', 'phone_number')
        }),
        ('PayPal Details', {
            'fields': ('paypal_order_id', 'paypal_capture_id', 'paypal_payer_email', 'paypal_webhook_event'),
            'classes': ('collapse',),
        }),
        ('Dates', {
            'fields': ('expiry_date', 'created_at', 'updated_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'completed': 'green', 'pending': 'orange',
            'failed': 'red', 'cancelled': 'gray', 'refunded': 'blue',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color:{};font-weight:bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def mark_completed_activate_pro(self, request, queryset):
        import datetime
        for tx in queryset:
            tx.status = 'completed'
            tx.save()
            profile, _ = Profile.objects.get_or_create(user=tx.user)
            days = 365 if tx.plan_type == 'annual' else 30
            profile.is_pro = True
            profile.pro_started_at = timezone.now()
            profile.pro_expires_at = timezone.now() + datetime.timedelta(days=days)
            profile.save()
        self.message_user(request, f"Marked {queryset.count()} transactions as completed and activated Pro.")
    mark_completed_activate_pro.short_description = "✅ Mark Completed + Activate Pro"

    def mark_failed(self, request, queryset):
        queryset.update(status='failed')
        self.message_user(request, f"Marked {queryset.count()} transactions as failed.")
    mark_failed.short_description = "❌ Mark as Failed"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"Marked {queryset.count()} transactions as cancelled.")
    mark_cancelled.short_description = "🚫 Mark as Cancelled"


# ─────────────────────────────────────────
#  90-DAY CHALLENGE
# ─────────────────────────────────────────
@admin.register(Routine90)
class Routine90Admin(admin.ModelAdmin):
    list_display = ('user', 'title', 'current_day', 'streak', 'is_active', 'completed', 'start_date', 'progress_pct')
    list_filter = ('is_active', 'completed')
    search_fields = ('user__username', 'title')
    readonly_fields = ('progress_percentage', 'days_remaining')

    def progress_pct(self, obj):
        return f"{obj.progress_percentage}%"
    progress_pct.short_description = 'Progress'


# ─────────────────────────────────────────
#  WEIGHT LOG
# ─────────────────────────────────────────
@admin.register(WeightLog)
class WeightLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'weight', 'date')
    list_filter = ('date', 'user')
    search_fields = ('user__username',)
    date_hierarchy = 'date'


# ─────────────────────────────────────────
#  CHAT MESSAGE
# ─────────────────────────────────────────
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_message', 'date')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'message', 'response')
    date_hierarchy = 'date'
    readonly_fields = ('date',)

    def short_message(self, obj):
        return obj.message[:80] + ('...' if len(obj.message) > 80 else '')
    short_message.short_description = 'Message'


# ─────────────────────────────────────────
#  NOTIFICATION
# ─────────────────────────────────────────
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    actions = ['mark_all_read']
    date_hierarchy = 'created_at'

    def mark_all_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"Marked {queryset.count()} notifications as read.")
    mark_all_read.short_description = "✅ Mark as Read"