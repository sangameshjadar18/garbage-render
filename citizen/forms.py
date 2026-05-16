from django import forms
from .models import Report


class ReportForm(forms.ModelForm):
    """Form for submitting a garbage complaint."""

    class Meta:
        model = Report
        fields = ['title', 'description', 'location', 'map_link', 'latitude', 'longitude', 'image', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief title of the issue',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the garbage issue in detail...',
                'rows': 4,
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address or landmark',
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
            }),
            'map_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Paste Google Maps link here',
            }),
        }

    def clean_map_link(self):
        map_link = self.cleaned_data.get('map_link')
        if map_link:
            import urllib.parse
            # Basic validation to ensure it looks like a URL
            result = urllib.parse.urlparse(map_link)
            if not all([result.scheme, result.netloc]):
                raise forms.ValidationError("Enter a valid map link")
            
            # Optionally restrict to google maps (just checking google or goo.gl is in netloc)
            if 'google' not in result.netloc and 'goo.gl' not in result.netloc:
                raise forms.ValidationError("Enter a valid map link")
        return map_link
