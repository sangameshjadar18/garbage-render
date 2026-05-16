from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
import re


class UserRegistrationForm(UserCreationForm):
    """Registration form with role selection."""

    REGISTER_ROLE_CHOICES = (
        ('citizen', 'Citizen'),
        ('worker', 'Worker'),
    )

    role = forms.ChoiceField(
        choices=REGISTER_ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    email = forms.EmailField(
        required=True,
        error_messages={'invalid': 'Enter a valid email address'}
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your address', 'rows': 2}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address', 'role', 'password1', 'password2']
        widgets = {
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure username validation styling is perfectly applied
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Username',
            'minlength': '4',
            'maxlength': '12',
            'pattern': '[A-Za-z]+',
            'required': 'required'
        })
        self.fields['username'].help_text = ''  # Clear Django's default username help text
        
        # Explicitly enforce email widget styling to override any template defaults
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Email address',
            'required': 'required'
        })
        
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})

    def save(self, commit=True):
        # Guarantee that email and other fields are mapped from form specifically
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            return username

        if len(username) < 4:
            raise forms.ValidationError("Username must be at least 4 characters")
        if len(username) > 12:
            raise forms.ValidationError("Username must not exceed 12 characters")
        if not username.isalpha():
            raise forms.ValidationError("Username must contain only alphabets")
            
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email

        # Validate email structure using regex
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email):
            raise forms.ValidationError("Enter a valid email address")

        # Extract domain and main domain logic
        try:
            domain_part = email.split('@')[1]
            main_domain = domain_part.split('.')[0]
        except IndexError:
            raise forms.ValidationError("Enter a valid email address")

        # Reject domains where main domain contains numbers
        if re.search(r'\d', main_domain):
            raise forms.ValidationError("Invalid email domain")
            
        # Ensure email is unique (case-insensitive)
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email already registered")
            
        return email


class UserLoginForm(AuthenticationForm):
    """Custom login form with styled inputs."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
    )


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
