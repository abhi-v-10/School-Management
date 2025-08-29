from django import forms


class LinkChildForm(forms.Form):
    email = forms.EmailField(
        label='Student Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter student email',
        })
    )

