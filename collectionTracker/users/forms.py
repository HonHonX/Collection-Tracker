# from ChatGPT
# form for register

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)        
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = False
        
        if commit:
            user.save()
        return user
    

class ProfileImageForm(forms.Form):
    image = forms.ImageField(required=True, max_length=2*1024*1024, error_messages={'max_length': 'Image file too large (maximum 2MB).'})

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

class CustomPasswordResetForm(PasswordResetForm):
    username = forms.CharField()

    def clean(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        User = get_user_model()
        
        if email and username:
            try:
                user = User.objects.get(email=email, username=username)
                self.user_cache = user
            except User.DoesNotExist:
                raise ValidationError("No user found with this email address and username.")
        return self.cleaned_data

    def get_users(self, email):
        if hasattr(self, 'user_cache'):
            return [self.user_cache]
        return []