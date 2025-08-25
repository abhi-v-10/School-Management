from django import forms
from .models import Exam

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['class_room', 'subject', 'exam_date', 'max_marks']
        widgets = {
            'class_room': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'exam_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
        }
