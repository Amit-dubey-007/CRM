from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email= forms.EmailField(required=True)
    class Meta:
        model=User
        fields=['email','password1','password2']

    def clean_email(self):
        email=self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")

        return email 

from django.contrib.auth.forms import AuthenticationForm

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your email",
        }),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your password",
        }),
    )