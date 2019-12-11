from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True,
                            widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bank_name', 'account_number')

    def clean_account_number(self):
        account_number = self.cleaned_data['account_number']
        if not account_number.isdigit():
            raise forms.ValidationError('Please enter digits only')
        if len(account_number) != 10:
            raise forms.ValidationError(
                'Please your bank account number should be 10 digits')
        return account_number
