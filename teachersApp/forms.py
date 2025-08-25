from django import forms
from .models import Teacher
from classesApp.models import ClassRoom, Subjects

class TeacherAdminForm(forms.ModelForm):
    subject = forms.ModelMultipleChoiceField(
        queryset=Subjects.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10})
    )
    assigned_class = forms.ModelMultipleChoiceField(
        queryset=ClassRoom.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10})
    )

    class Meta:
        model = Teacher
        fields = ['subject', 'assigned_class']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance
