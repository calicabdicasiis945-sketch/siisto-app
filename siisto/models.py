from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    dhererka = models.FloatField(blank=True, null=True, help_text="Height in cm")
    da_da = models.IntegerField(blank=True, null=True, help_text="Age in years")
    jinsiga = models.CharField(max_length=20, blank=True, null=True, choices=(('male', 'Lab / Male'), ('female', 'Dhedig / Female')))
    hadafka = models.CharField(max_length=100, blank=True, null=True, help_text="Fitness Goal")
    heerka_dhaqdhaqaaqa = models.CharField(max_length=50, blank=True, null=True, help_text="Activity Level")
    miisaanka_yoolka = models.FloatField(blank=True, null=True, help_text="Target Goal Weight in kg")
    onboarding_completed = models.BooleanField(default=False)
    is_pro = models.BooleanField(default=False)
    pro_expires_at = models.DateTimeField(blank=True, null=True)

    @property
    def miisaan_hadda(self):
        latest_log = WeightLog.objects.filter(user=self.user).order_by('-date').first()
        return latest_log.weight if latest_log else None

    @property
    def has_active_pro(self):
        if not self.is_pro:
            return False
        if self.pro_expires_at and self.pro_expires_at < timezone.now():
            return False
        return True

    def __str__(self):
        return f"Profile of {self.user.username}"


class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    calories = models.IntegerField()
    protein = models.FloatField(default=0.0)
    carbs = models.FloatField(default=0.0)
    fats = models.FloatField(default=0.0)
    image = models.ImageField(upload_to='meal_images/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.calories} kcal) - {self.user.username}"


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

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Chest')
    subcategory = models.CharField(max_length=50, blank=True, default='General')
    description = models.TextField(blank=True, default='')
    image_url = models.URLField(max_length=500, blank=True, null=True)
    video_3d_url = models.CharField(max_length=500, blank=True, null=True, help_text="Pinterest, YouTube, or 3D Video animation link")
    target_muscle = models.CharField(max_length=150, blank=True, default='')
    correct_form_instructions = models.TextField(blank=True, default='')
    default_duration = models.IntegerField(default=15)
    default_sets = models.IntegerField(default=4)
    default_reps = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.name} ({self.category} - {self.subcategory})"


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(ExerciseLibrary, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    duration = models.IntegerField(default=15)  # minutes
    sets = models.IntegerField(default=4)
    reps = models.IntegerField(default=10)
    weight_kg = models.FloatField(default=0.0)
    video_3d_url = models.CharField(max_length=500, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.duration} mins) - {self.user.username}"


class WeightLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.weight} kg on {self.date.strftime('%Y-%m-%d')}"


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    is_ai = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat with {self.user.username} on {self.date.strftime('%Y-%m-%d %H:%M')}"


class Routine90(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='Routine Title')
    completed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class PaymentTransaction(models.Model):
    STATUS_CHOICES = (
        ('completed', 'Paid / Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan_name = models.CharField(max_length=100, default='Skillset Pro Monthly')
    amount = models.FloatField(default=10.00)
    currency = models.CharField(max_length=10, default='USD')
    payment_method = models.CharField(max_length=50, default='EVC Plus')
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.status}) - {self.transaction_id}"