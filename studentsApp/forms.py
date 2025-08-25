from django import forms
from .models import Student

class StudentAdminForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['class_room', 'parent']   # add your real fields here
        widgets = {
            'class_room': forms.Select(attrs={'class': 'form-select'}),
            'parent': forms.TextInput(attrs={'class': 'form-control'}),
        }
