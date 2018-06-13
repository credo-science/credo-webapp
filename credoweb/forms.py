from __future__ import unicode_literals
from django import forms


class RegistrationForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField(min_length=3, max_length=50)
    display_name = forms.CharField(min_length=3, max_length=50)
    team = forms.CharField(max_length=50)
    password = forms.CharField(min_length=6, max_length=128, widget=forms.PasswordInput())
    confirm_password = forms.CharField(min_length=6, max_length=128, widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        if not (cleaned_data.get('password') == cleaned_data.get('confirm_password')):
            self.add_error('password_confirm', 'Passwords do not match')
