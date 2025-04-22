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
        fields = ['title', 'description', 'location', 'company_name', 'salary_min', 'salary_max', 'is_active']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio']  # Only the fields specific to the profile

class JobSearchForm(forms.Form):
    query = forms.CharField(required=False, label='Search', widget=forms.TextInput(attrs={'placeholder': 'Search jobs...'}))
    location = forms.CharField(required=False)
    salary_min = forms.DecimalField(required=False, min_value=0)
    salary_max = forms.DecimalField(required=False, min_value=0)
    experience_level = forms.ChoiceField(required=False, choices=[('', 'All'), ('junior', 'Junior'), ('mid', 'Mid'), ('senior', 'Senior')])
    job_type = forms.ChoiceField(required=False, choices=[('', 'All'), ('full-time', 'Full-time'), ('part-time', 'Part-time')])