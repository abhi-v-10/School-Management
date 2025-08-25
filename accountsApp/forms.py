from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth import get_user_model
from parentsApp.models import Parent

class AdminRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin'
        if commit:
            user.save()
        return user
    
class TeacherRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'
        if commit:
            user.save()
        return user
    
class StudentRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
        return user

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'message']

class ParentRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'parent'
        if commit:
            user.save()
        return user

User = get_user_model()

class ProfileForm(forms.ModelForm):
    # this field is for Parent users only; we'll hide it for others
    phone_number = forms.CharField(
        max_length=15, required=False, label="Mobile Number",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mobile'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']  # your custom User has `role` but no mobile
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance

        # Only show & prefill phone number for parents
        if user and getattr(user, 'role', None) == 'parent':
            try:
                parent = Parent.objects.get(user=user)
                self.fields['phone_number'].initial = parent.phone_number
            except Parent.DoesNotExist:
                pass
        else:
            # not a parent → remove the field from the form entirely
            self.fields.pop('phone_number', None)

    def save(self, commit=True):
        user = super().save(commit=commit)
        # persist parent's phone if applicable
        if getattr(user, 'role', None) == 'parent' and 'phone_number' in self.cleaned_data:
            parent, _ = Parent.objects.get_or_create(user=user)
            parent.phone_number = self.cleaned_data.get('phone_number', '') or ''
            parent.save()
        return user
