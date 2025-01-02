from django import forms

class ProfileImageForm(forms.Form):
    image = forms.ImageField(required=True, max_length=2*1024*1024, error_messages={'max_length': 'Image file too large (maximum 2MB).'})
