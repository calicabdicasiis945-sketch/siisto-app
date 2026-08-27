from django import forms
from .models import Meal, Workout, WeightLog, Profile


class MealForm(forms.ModelForm):
    """Form for logging a meal with macro nutrients."""
    class Meta:
        model = Meal
        fields = ['name', 'calories', 'protein', 'carbs', 'fats', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'E.g. Baasto iyo Hilib, Rice & Chicken...'}),
            'calories': forms.NumberInput(attrs={'placeholder': 'kcal', 'min': 0}),
            'protein': forms.NumberInput(attrs={'placeholder': 'g', 'step': '0.1', 'min': 0}),
            'carbs': forms.NumberInput(attrs={'placeholder': 'g', 'step': '0.1', 'min': 0}),
            'fats': forms.NumberInput(attrs={'placeholder': 'g', 'step': '0.1', 'min': 0}),
        }


class WorkoutForm(forms.ModelForm):
    """Form for logging a workout session."""
    class Meta:
        model = Workout
        fields = ['name', 'duration', 'sets', 'reps', 'weight_kg', 'body_part', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'E.g. Bench Press, Squats...'}),
            'duration': forms.NumberInput(attrs={'placeholder': 'Minutes', 'min': 1}),
            'sets': forms.NumberInput(attrs={'placeholder': 'Sets', 'min': 1}),
            'reps': forms.NumberInput(attrs={'placeholder': 'Reps', 'min': 1}),
            'weight_kg': forms.NumberInput(attrs={'placeholder': 'kg', 'step': '0.5', 'min': 0}),
            'body_part': forms.TextInput(attrs={'placeholder': 'E.g. Chest, Back, Legs...'}),
            'notes': forms.Textarea(attrs={'placeholder': 'Optional notes...', 'rows': 2}),
        }


class WeightLogForm(forms.ModelForm):
    """Form to log current body weight."""
    class Meta:
        model = WeightLog
        fields = ['weight']
        widgets = {
            'weight': forms.NumberInput(attrs={
                'placeholder': 'Enter weight in kg',
                'step': '0.1',
                'min': 20,
                'max': 500,
            }),
        }


class ProfileForm(forms.ModelForm):
    """Form to update the user profile with fitness information."""
    class Meta:
        model = Profile
        fields = [
            'dhererka',          # height cm
            'da_da',             # age
            'jinsiga',           # gender
            'birth_date',
            'preferred_language',
            'hadafka',           # fitness goal
            'heerka_dhaqdhaqaaqa',  # activity level
            'miisaanka_yoolka',  # target weight kg
            'fitness_level',
            'experience_level',
            'bio',
            'location',
        ]
        widgets = {
            'dhererka': forms.NumberInput(attrs={'placeholder': 'Height in cm', 'step': '0.1'}),
            'da_da': forms.NumberInput(attrs={'placeholder': 'Age in years', 'min': 10, 'max': 100}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'miisaanka_yoolka': forms.NumberInput(attrs={'placeholder': 'Target weight in kg', 'step': '0.1'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Tell us about yourself...', 'rows': 3}),
            'location': forms.TextInput(attrs={'placeholder': 'Your city/country'}),
        }
        labels = {
            'dhererka': 'Height (cm)',
            'da_da': 'Age',
            'jinsiga': 'Gender',
            'birth_date': 'Date of Birth',
            'preferred_language': 'Language / Luqadda',
            'hadafka': 'Fitness Goal',
            'heerka_dhaqdhaqaaqa': 'Activity Level',
            'miisaanka_yoolka': 'Target Weight (kg)',
            'fitness_level': 'Fitness Level',
            'experience_level': 'Experience Level',
            'bio': 'About Me',
            'location': 'Location',
        }