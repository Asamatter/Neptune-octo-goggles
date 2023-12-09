from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import EmailValidator  # Import EmailValidator


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['banner', 'pic', 'website', 'bio', 'location']


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, validators=[EmailValidator()])  # Add EmailValidator to the email field

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email


class InboxForm(forms.ModelForm):
    class Meta:
        model = Inbox
        fields = ['content']


class CircleCreationForm(forms.ModelForm):
    class Meta:
        model = Circle
        fields = ['pfp', 'name', 'description', 'privacy']


class CirclePostForm(forms.ModelForm):
    class Meta:
        model = CirclePost
        fields = ['title', 'img']
