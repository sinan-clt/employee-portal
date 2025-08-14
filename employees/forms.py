from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser, FormTemplate, FormField

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2')

class CustomPasswordChangeForm(PasswordChangeForm):
    pass

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'profile_picture')

class FormTemplateForm(forms.ModelForm):
    class Meta:
        model = FormTemplate
        fields = ('name',)

class FormFieldForm(forms.ModelForm):
    class Meta:
        model = FormField
        fields = ('label', 'field_type', 'required')