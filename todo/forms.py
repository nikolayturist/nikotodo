from django.forms import ModelForm
from .models import Todo
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class TodoForm(ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'due_date', 'completed_date', 'importance']
        due_date = forms.DateField(
            widget=forms.DateInput(format='%m/%d/%Y'),
            input_formats=('%m/%d/%Y',)
        )


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=50,
                               label="User name",
                               required=True,
                               initial="Your name",
                               widget=(forms.TextInput(attrs={'class': 'form-control'}))
                               )
    email = forms.EmailField(max_length=254,
                             required=True,
                             initial="example@test.com",
                             widget=(forms.TextInput(attrs={'class': 'form-control'})))

    password1 = forms.CharField(label="Password",
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    password2 = forms.CharField(label="Password Confirmation",
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("Username already exists. Please try another name.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)

        validate_email(email)

        if r.count():
            raise ValidationError("Email already exists. Please try another email.")

        return email

    def clean_password1(self):
        return self.cleaned_data.get('password1')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords didn't match.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active
        if commit:
            user.save()
        return user

