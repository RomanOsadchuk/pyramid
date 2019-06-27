from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django import forms

from .models import Profile
from .tokens import sign_up_token_generator


class SignInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

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
    invitation_code = forms.CharField()

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
        if not Profile.objects.filter(invitation_code=code).exists():
            raise ValidationError('This code is invalid')
        return code

    def clean(self):
        if 'password' in self.cleaned_data:
            # password is valid
            password = self.cleaned_data['password']
            password2 = self.cleaned_data['password2']
            if password != password2:
                raise ValidationError('Passwords do not match')

    def create_user(self, generate_token=True):
        """
        This method saves inactive user and returns this user object.
        If generate_token is True - attaching confirmation token it.
        Use if form is valid.
        """
        user = User.objects.create_user(username=self.cleaned_data['email'],
                                        email=self.cleaned_data['email'],
                                        password=self.cleaned_data['password'])
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False
        user.save()

        if generate_token:
            code = self.cleaned_data['invitation_code']
            user.token = sign_up_token_generator.make_token(user, code)
        return user
