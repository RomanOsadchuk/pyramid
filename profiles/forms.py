from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Profile
from .tokens import make_confirmation_token
from .utils import send_confirmation_email


class SignInForm(forms.Form):
    """
    Has additional user field to store authenticated user there
    if credentials are right.
    """
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = authenticate(username=email, password=password)
        if user is None:
            raise ValidationError('Invalid credentials')
        self.user = user


class SignUpForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label='Confirm Password')
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    invitation_code = forms.CharField(required=False)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email already signed up')
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)
        return password

    def clean_invitation_code(self):
        code = self.cleaned_data['invitation_code']
        if Profile.objects.all().count() < settings.NO_CODE_REQUIRED_COUNT:
            return code
        if not code:
            raise ValidationError('Invitation code is required')
        if not Profile.objects.filter(invitation_code=code).exists():
            raise ValidationError('This code is invalid')
        return code

    def clean(self):
        if 'password' in self.cleaned_data: # password is valid and secure
            password = self.cleaned_data['password']
            password2 = self.cleaned_data['password2']
            if password != password2:
                raise ValidationError('Passwords do not match')

    def create_inactive_user(self, send_email=True):
        """
        This method saves inactive user and returns created user object.
        If send_email is True - also sending confirmation email.
        """
        user = User.objects.create_user(username=self.cleaned_data['email'],
                                        email=self.cleaned_data['email'],
                                        password=self.cleaned_data['password'])
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False
        user.save()

        if send_email:
            code = self.cleaned_data['invitation_code']
            token = make_confirmation_token(user, code)
            send_confirmation_email(self.cleaned_data['email'], token)
        return user
