from django import forms
from .models import Resource
from classesApp.models import ClassRoom

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'class_room', 'subject', 'file', 'resource_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'description': forms.Textarea(attrs={'rows':3, 'class':'form-control', 'placeholder':'Short description'}),
            'class_room': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'resource_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            # Limit class_room and subject choices to teacher's assignments
            self.fields['class_room'].queryset = teacher.assigned_class.all()
            self.fields['subject'].queryset = teacher.subject.all()