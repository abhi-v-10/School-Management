from django import forms
from .models import Student

class StudentAdminForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['class_room', 'parent_email', 'parent']
        widgets = {
            'class_room': forms.Select(attrs={'class': 'form-select'}),
            'parent_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_parent_email(self):
        email = self.cleaned_data.get('parent_email')
        return email.lower() if email else email
