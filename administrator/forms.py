from django import forms
from .models import GarbageBin
from accounts.models import User


class GarbageBinForm(forms.ModelForm):
    """Form for creating/editing garbage bins."""

    class Meta:
        model = GarbageBin
        fields = ['location', 'latitude', 'longitude', 'waste_type', 'capacity', 'status', 'assigned_worker']
        widgets = {
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bin location address'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Latitude', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Longitude', 'step': '0.000001'}),
            'waste_type': forms.Select(attrs={'class': 'form-select'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_worker': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_worker'].queryset = User.objects.filter(role='worker', is_active=True)
        self.fields['assigned_worker'].required = False


class AssignWorkerForm(forms.Form):
    """Form for assigning a worker to a report."""

    worker = forms.ModelChoiceField(
        queryset=User.objects.filter(role='worker', is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Select a worker',
    )
    priority = forms.ChoiceField(
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
