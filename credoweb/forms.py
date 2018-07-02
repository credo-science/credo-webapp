from __future__ import unicode_literals

from datetime import datetime

from django import forms


class RegistrationForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField(min_length=3, max_length=50)
    display_name = forms.CharField(min_length=3, max_length=50)
    team = forms.CharField(max_length=50)
    password = forms.CharField(min_length=6, max_length=128, widget=forms.PasswordInput())
    confirm_password = forms.CharField(min_length=6, max_length=128, widget=forms.PasswordInput())
    accept_rules = forms.BooleanField()

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        if not (cleaned_data.get('password') == cleaned_data.get('confirm_password')):
            self.add_error('password_confirm', 'Passwords do not match')
        if not cleaned_data.get('accept_rules'):
            self.add_error('accept_rules', 'Please accept the rules')


class ContestCreationForm(forms.Form):
    name = forms.CharField(min_length=3, max_length=128, label='Contest name')
    start_time = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M:%S'], initial=datetime.now())
    duration = forms.IntegerField(min_value=1, max_value=24*7, initial=24, label='Duration (h)')
    limit = forms.IntegerField(min_value=10, max_value=100, initial=20, label='Limit of recent detections displayed')
    avbrightness_max = forms.FloatField(min_value=0, max_value=1, initial=0.01,
                                        label='Average brightness', label_suffix=' <')
    maxbrightness_min = forms.IntegerField(min_value=0, max_value=255, initial=120,
                                           label='Maximum single pixel brightness', label_suffix=' >')
