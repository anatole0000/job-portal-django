from django import forms
from .models import Application
from .models import Job
from .models import UserProfile

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']  # Only allow changing the status


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'company_name', 'salary', 'is_active']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio']  # Only the fields specific to the profile