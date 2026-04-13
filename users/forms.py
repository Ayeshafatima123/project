from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, UserProfile


class UserRegistrationForm(forms.ModelForm):
    """User registration form"""
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'Confirm Password'
    }))
    referral_code = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'Referral Code (optional)'
    }))
    country = forms.ChoiceField(choices=[
        ('Pakistan', 'Pakistan'),
        ('India', 'India'),
        ('Bangladesh', 'Bangladesh'),
        ('United States', 'United States'),
        ('United Kingdom', 'United Kingdom'),
        ('Other', 'Other'),
    ], widget=forms.Select(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
    }))

    class Meta:
        model = User
        fields = ['email', 'username', 'phone', 'password', 'confirm_password', 'referral_code', 'country']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Email Address'
            }),
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Username'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Phone Number (optional)'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match')

        return cleaned_data


class UserLoginForm(AuthenticationForm):
    """User login form"""
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'Email Address'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'Password'
    }))


class ProfileForm(forms.ModelForm):
    """User profile form"""
    class Meta:
        model = UserProfile
        fields = ['country', 'city', 'address', 'date_of_birth', 'profile_picture']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
