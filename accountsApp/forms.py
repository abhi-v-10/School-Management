from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth import get_user_model
from parentsApp.models import Parent
from django.contrib.auth import password_validation

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
    parent_email = forms.EmailField(required=False, label="Parent Email",
                                    widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Parent's email (optional)"}))
    class Meta:
        model = User
        fields = ['username', 'email', 'parent_email', 'password1', 'password2']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
            # attach parent_email to auto-created Student profile if provided
            from studentsApp.models import Student  # local import to avoid circular
            try:
                student = Student.objects.get(user=user)
                pe = self.cleaned_data.get('parent_email')
                if pe:
                    student.parent_email = pe.lower()
                    student.save()
            except Exception:
                pass
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
    profile_photo = forms.ImageField(required=False, label="Profile Photo",
                                     widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'profile_photo']  # your custom User has `role` but no mobile
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

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        if photo and photo.size > 5 * 1024 * 1024:  # 5MB
            raise forms.ValidationError("Image must be 5MB or smaller.")
        return photo

    def save(self, commit=True):
        user = super().save(commit=commit)
        # persist parent's phone if applicable
        if getattr(user, 'role', None) == 'parent' and 'phone_number' in self.cleaned_data:
            parent, _ = Parent.objects.get_or_create(user=user)
            parent.phone_number = self.cleaned_data.get('phone_number', '') or ''
            parent.save()
        return user

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter current password'}),
        required=True
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
        required=True
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Current password is incorrect.')
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                self.add_error('new_password2', 'Passwords do not match.')
            if current_password and password1 == current_password:
                self.add_error('new_password1', 'New password cannot be the same as the current password.')
            password_validation.validate_password(password1, self.user)
        return cleaned_data
