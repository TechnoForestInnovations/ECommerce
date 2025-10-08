from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import Profile

class NameEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','email']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder':'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder':'Last name'}),
            'email': forms.EmailInput(attrs={'placeholder':'you@example.com'}),
        }

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

class ProfileContactForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone']
        widgets = {'phone': forms.TextInput(attrs={'placeholder':'+91 9876543210'})}
