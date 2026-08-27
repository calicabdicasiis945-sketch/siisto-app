from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


# ─────────────────────────────────────────
#  PROFILE
# ─────────────────────────────────────────
class Profile(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male / Lab'),
        ('female', 'Female / Dhedig'),
    )
    GOAL_CHOICES = (
        ('lose_weight', 'Lose Weight / Miisaan Dhimis'),
        ('build_muscle', 'Build Muscle / Muruq Dhis'),
        ('maintain', 'Maintain / Joogteyn'),
        ('athletic_endurance', 'Athletic Endurance / Awood'),
        ('fat_loss', 'Fat Loss / Xoqid Dufanka'),
        ('muscle_gain', 'Muscle Gain / Kordhin Muruqa'),
        ('fitness', 'General Fitness / Caafimaad Guud'),
    )
    ACTIVITY_CHOICES = (
        ('sedentary', 'Sedentary / Fadhiga kaliya'),
        ('moderate', 'Moderate / Dhaqdhaqaaq Dhexdhexaad ah'),
        ('active', 'Active / Firfircoon'),
        ('very_active', 'Very Active / Aad u firfircoon'),
    )
    FITNESS_LEVEL_CHOICES = (
        ('beginner', 'Beginner / Bilowle'),
        ('intermediate', 'Intermediate / Dhexdhexaad'),
        ('advanced', 'Advanced / Horumarsan'),
        ('elite', 'Elite / Khabiir'),
    )
    EXPERIENCE_CHOICES = (
        ('none', 'No Experience'),
        ('less_1y', 'Less than 1 year'),
        ('1_3y', '1–3 years'),
        ('3_5y', '3–5 years'),
        ('5plus', '5+ years'),
    )

    LANGUAGE_CHOICES = (
        ('so', 'Somali / Soomaali'),
        ('en', 'English'),
        ('ar', 'Arabic / العربية'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    preferred_language = models.CharField(max_length=10, default='so', choices=LANGUAGE_CHOICES, help_text="Preferred UI language")

    # Fitness profile fields (Somali field names kept for migration continuity)
    dhererka = models.FloatField(blank=True, null=True, help_text="Height in cm")
    da_da = models.IntegerField(blank=True, null=True, help_text="Age in years")
    jinsiga = models.CharField(max_length=20, blank=True, null=True, choices=GENDER_CHOICES)
    hadafka = models.CharField(max_length=100, blank=True, null=True, choices=GOAL_CHOICES, help_text="Fitness Goal")
    heerka_dhaqdhaqaaqa = models.CharField(max_length=50, blank=True, null=True, choices=ACTIVITY_CHOICES, help_text="Activity Level")
    miisaanka_yoolka = models.FloatField(blank=True, null=True, help_text="Target Goal Weight in kg")
    fitness_level = models.CharField(max_length=20, blank=True, null=True, choices=FITNESS_LEVEL_CHOICES, default='beginner')
    experience_level = models.CharField(max_length=20, blank=True, null=True, choices=EXPERIENCE_CHOICES, default='none')

    # Account status
    onboarding_completed = models.BooleanField(default=False)
    is_pro = models.BooleanField(default=False)
    pro_expires_at = models.DateTimeField(blank=True, null=True)
    pro_started_at = models.DateTimeField(blank=True, null=True)

    @property
    def language(self):
        return self.preferred_language or 'so'

    @language.setter
    def language(self, val):
        self.preferred_language = val

    # English aliases for Somali field names
    @property
    def height(self):
        return self.dhererka

    @height.setter
    def height(self, value):
        self.dhererka = value

    @property
    def gender(self):
        return self.jinsiga

    @gender.setter
    def gender(self, value):
        self.jinsiga = value

    @property
    def goal(self):
        return self.hadafka

    @goal.setter
    def goal(self, value):
        self.hadafka = value

    @property
    def fitness_goal(self):
        return self.hadafka

    @property
    def activity_level(self):
        return self.heerka_dhaqdhaqaaqa

    @activity_level.setter
    def activity_level(self, value):
        self.heerka_dhaqdhaqaaqa = value

    @property
    def target_weight(self):
        return self.miisaanka_yoolka

    @target_weight.setter
    def target_weight(self, value):
        self.miisaanka_yoolka = value

    # Computed: current weight from latest WeightLog
    @property
    def miisaan_hadda(self):
        latest_log = WeightLog.objects.filter(user=self.user).order_by('-date').first()
        return latest_log.weight if latest_log else None

    # English alias for current weight
    @property
    def current_weight(self):
        return self.miisaan_hadda

    @property
    def has_active_pro(self):
        if not self.is_pro:
            return False
        if self.pro_expires_at and self.pro_expires_at < timezone.now():
            return False
        return True

    @property
    def age(self):
        """Compute age from birth_date if da_da not set."""
        if self.da_da:
            return self.da_da
        if self.birth_date:
            today = timezone.now().date()
            return (today - self.birth_date).days // 365
        return None

    def __str__(self):
        return f"Profile of {self.user.username}"


# ─────────────────────────────────────────
#  MEAL
# ─────────────────────────────────────────
class Meal(models.Model):
    MEAL_TYPE_CHOICES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meals')
    name = models.CharField(max_length=200, default='Meal')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, default='lunch', blank=True)
    calories = models.IntegerField(default=0)
    protein = models.FloatField(default=0.0)
    carbs = models.FloatField(default=0.0)
    fats = models.FloatField(default=0.0)
    image = models.ImageField(upload_to='meal_images/', blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} ({self.calories} kcal) - {self.user.username}"


# ─────────────────────────────────────────
#  EXERCISE LIBRARY
# ─────────────────────────────────────────
class ExerciseLibrary(models.Model):
    CATEGORY_CHOICES = (
        ('Chest', 'Chest / Xabadka'),
        ('Back', 'Back / Dhabarka'),
        ('Shoulders', 'Shoulders / Garabka'),
        ('Arms', 'Arms / Gacmaha'),
        ('Legs', 'Legs / Lugaha'),
        ('Abs / Core', 'Abs & Core / Caloosha'),
        ('Cardio', 'Cardio / Wadnaha & Orodka'),
    )
    DIFFICULTY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Chest')
    subcategory = models.CharField(max_length=50, blank=True, default='General')
    description = models.TextField(blank=True, default='')
    correct_form_instructions = models.TextField(blank=True, default='')
    target_muscle = models.CharField(max_length=150, blank=True, default='')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')

    # Media — local files (preferred)
    image = models.ImageField(upload_to='exercise_images/', blank=True, null=True)
    video_file = models.FileField(
        upload_to='exercise_videos/',
        blank=True, null=True,
        help_text="Upload local MP4 video file for 3D demonstration"
    )

    # Legacy URL fields (kept for backwards compatibility)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    video_3d_url = models.CharField(
        max_length=500, blank=True, null=True,
        help_text="Legacy: external video URL (overridden by video_file if both present)"
    )

    # Defaults for workout logging
    default_duration = models.IntegerField(default=15)
    default_sets = models.IntegerField(default=4)
    default_reps = models.IntegerField(default=10)

    class Meta:
        ordering = ['category', 'subcategory', 'name']

    def __str__(self):
        return f"{self.name} ({self.category} - {self.subcategory})"

    @property
    def video_url(self):
        """Standard alias for video_3d_url."""
        return self.video_3d_url or ''

    @video_url.setter
    def video_url(self, value):
        self.video_3d_url = value

    @property
    def display_video_url(self):
        """Returns the best available video source."""
        if self.video_file:
            return self.video_file.url
        return self.video_3d_url or None

    @property
    def display_image_url(self):
        """Returns the best available image source."""
        if self.image:
            return self.image.url
        return self.image_url or None

    def get_video_embed_info(self):
        """
        Parses video_file / video_3d_url and returns structured embed information:
        - type: 'file' | 'youtube' | 'vimeo' | 'pinterest' | 'direct_video' | 'external' | 'none'
        - src: embed URL, file URL, or external link
        """
        import re
        if self.video_file:
            return {'type': 'file', 'src': self.video_file.url}

        url = (self.video_3d_url or '').strip()
        if not url:
            return {'type': 'none', 'src': None}

        # Direct video files (.mp4, .webm, .mov, etc.)
        if any(url.lower().endswith(ext) or f"{ext}?" in url.lower() for ext in ['.mp4', '.webm', '.ogg', '.mov']):
            return {'type': 'direct_video', 'src': url}

        # YouTube
        yt_match = re.search(r'(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})', url)
        if yt_match:
            yt_id = yt_match.group(1)
            return {
                'type': 'youtube',
                'video_id': yt_id,
                'src': f"https://www.youtube-nocookie.com/embed/{yt_id}?autoplay=1&mute=1&loop=1&playlist={yt_id}&controls=1"
            }

        # Vimeo
        vimeo_match = re.search(r'vimeo\.com\/(?:video\/)?([0-9]+)', url)
        if vimeo_match:
            v_id = vimeo_match.group(1)
            return {
                'type': 'vimeo',
                'video_id': v_id,
                'src': f"https://player.vimeo.com/video/{v_id}?autoplay=1&loop=1&muted=1"
            }

        # Pinterest Pin or Video URL
        if 'pinterest.com' in url.lower():
            return {'type': 'pinterest', 'src': url}

        # Generic External URL
        return {'type': 'external', 'src': url}


# ─────────────────────────────────────────
#  WORKOUT
# ─────────────────────────────────────────
class Workout(models.Model):
    BODY_PART_CHOICES = (
        ('Chest', 'Chest / Xabadka'),
        ('Back', 'Back / Dhabarka'),
        ('Shoulders', 'Shoulders / Garabka'),
        ('Biceps', 'Biceps / Gacanta Hore'),
        ('Triceps', 'Triceps / Gacanta Dambe'),
        ('Forearms', 'Forearms / Reedhaha'),
        ('Quadriceps', 'Quadriceps / Karka Hore'),
        ('Hamstrings', 'Hamstrings / Karka Dambe'),
        ('Glutes', 'Glutes / Xoqida'),
        ('Calves', 'Calves / Caloosha Lugta'),
        ('Abs', 'Abs / Caloosha'),
        ('Core', 'Core / Bartamaha Jirka'),
        ('Cardio', 'Cardio / Wadnaha'),
        ('Full Body', 'Full Body / Jirka Oo Dhan'),
        ('Other', 'Other / Kale'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    exercise = models.ForeignKey(ExerciseLibrary, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200, default='Workout')
    body_part = models.CharField(max_length=50, choices=BODY_PART_CHOICES, blank=True, default='Other')
    duration = models.IntegerField(default=15, help_text="Duration in minutes")
    sets = models.IntegerField(default=4)
    reps = models.IntegerField(default=10)
    weight_kg = models.FloatField(default=0.0)
    notes = models.TextField(blank=True, default='')
    video_3d_url = models.CharField(max_length=500, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} ({self.duration} mins) - {self.user.username}"


# ─────────────────────────────────────────
#  WEIGHT LOG
# ─────────────────────────────────────────
class WeightLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weight_logs')
    weight = models.FloatField()
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username}: {self.weight} kg on {self.date.strftime('%Y-%m-%d')}"


# ─────────────────────────────────────────
#  CHAT MESSAGE
# ─────────────────────────────────────────
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    response = models.TextField()
    is_ai = models.BooleanField(default=True)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"Chat with {self.user.username} on {self.date.strftime('%Y-%m-%d %H:%M')}"


# ─────────────────────────────────────────
#  90-DAY CHALLENGE
# ─────────────────────────────────────────
class Routine90(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenge_90')
    title = models.CharField(max_length=200, default='90-Day Fitness Challenge')
    is_active = models.BooleanField(default=True)
    completed = models.BooleanField(default=False)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    current_day = models.IntegerField(default=1)
    streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    target_workouts_per_week = models.IntegerField(default=5)
    last_activity_date = models.DateField(blank=True, null=True)

    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.user.username} (Day {self.current_day})"

    @property
    def progress_percentage(self):
        return min(int((self.current_day / 90) * 100), 100)

    @property
    def days_remaining(self):
        return max(90 - self.current_day, 0)

    def save(self, *args, **kwargs):
        if self.start_date and not self.end_date:
            from datetime import date, timedelta
            self.end_date = self.start_date + timedelta(days=89)
        super().save(*args, **kwargs)


# ─────────────────────────────────────────
#  PAYMENT TRANSACTION
# ─────────────────────────────────────────
class PaymentTransaction(models.Model):
    STATUS_CHOICES = (
        ('completed', 'Completed / Paid'),
        ('pending', 'Pending / Waiting'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('paypal', 'PayPal'),
        ('evc_plus', 'EVC Plus (Hormuud)'),
        ('zaad', 'Zaad (Telesom)'),
        ('sahal', 'Sahal (Golis)'),
        ('other', 'Other'),
    )
    PLAN_CHOICES = (
        ('monthly', 'Siisto Pro Monthly — $9.99'),
        ('annual', 'Siisto Pro Annual — $89.99'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan_name = models.CharField(max_length=100, default='Siisto Pro Monthly')
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, default='monthly')
    amount = models.FloatField(default=9.99)
    currency = models.CharField(max_length=10, default='USD')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='paypal')
    phone_number = models.CharField(max_length=30, blank=True, null=True)

    # Internal reference
    transaction_id = models.CharField(max_length=100, unique=True)

    # PayPal-specific fields
    paypal_order_id = models.CharField(max_length=100, blank=True, null=True)
    paypal_capture_id = models.CharField(max_length=100, blank=True, null=True)
    paypal_payer_email = models.EmailField(blank=True, null=True)
    paypal_webhook_event = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expiry_date and self.status == 'completed':
            days = 365 if self.plan_type == 'annual' else 30
            self.expiry_date = timezone.now() + timedelta(days=days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.status}) - {self.transaction_id}"


# ─────────────────────────────────────────
#  NOTIFICATION
# ─────────────────────────────────────────
class Notification(models.Model):
    TYPE_CHOICES = (
        ('workout', 'Workout Reminder'),
        ('meal', 'Meal Reminder'),
        ('weight', 'Weight Log Reminder'),
        ('challenge', '90-Day Challenge'),
        ('premium', 'Premium Expiry'),
        ('system', 'System'),
        ('achievement', 'Achievement'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=200, blank=True, default='')
    scheduled_for = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title} → {self.user.username}"