from django import forms
from .models import Resource, ResourceRating
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

class ResourceRatingForm(forms.ModelForm):
    class Meta:
        model = ResourceRating
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows':2, 'placeholder':'Optional comment', 'class':'form-control'})
        }
    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput(attrs={'class':'form-control', 'placeholder':'1-5'}))

