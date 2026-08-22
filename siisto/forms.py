from django import forms
from .models import Cunto, Jimicsi, Profile, WeightLog

# 1. FOOMKA CUNTADA (Waxaan ku darnay Calories iyo Protein)
class CuntoForm(forms.ModelForm):
    class Meta:
        model = Cunto
        fields = ['nooca_cuntada', 'calories', 'protein']

# 2. FOOMKA JIMICSIGA
class JimicsiForm(forms.ModelForm):
    class Meta:
        model = Jimicsi
        fields = ['magaca_jimicsiga']

# 3. FOOMKA MIISAANKA (Weight Tracker)
class WeightLogForm(forms.ModelForm):
    class Meta:
        model = WeightLog
        fields = ['miisaanka']

# 4. FOOMKA PROFILE-KA (User Profile)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['dherer', 'miisaan_hadda', 'hadaf', 'avatar']