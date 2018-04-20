from __future__ import unicode_literals

from django.contrib.auth import get_user_model

from rest_framework import exceptions

User = get_user_model()

"""
Authentication example:

from django.contrib.auth import authenticate

user = authenticate(None, token='aaaa01')
"""


class TokenBackend(object):
    @staticmethod
    def authenticate(request, token=None):
        if not token:
            auth = request.META.get('HTTP_AUTHORIZATION')
            if not auth:
                raise exceptions.AuthenticationFailed('Missing authorization header')
            auth = auth.split()
            if len(auth) != 2 or auth[0] != 'Token':
                raise exceptions.AuthenticationFailed('Invalid authorization header')
            token = auth[1]

        if token:
            try:
                return User.objects.get(key=token), None
            except User.DoesNotExist:
                return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
