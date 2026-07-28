from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg bg-dark text-white border-secondary',
        'placeholder': 'Enter username',
        'id': 'username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg bg-dark text-white border-secondary',
        'placeholder': 'Enter password',
        'id': 'password'
    }))

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}), required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}), required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 3}), required=False)
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}), required=False)

    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'avatar']

class UserCreateForm(forms.ModelForm):
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
        }
