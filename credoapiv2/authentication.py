# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model

from rest_framework import authentication
from rest_framework import exceptions

User = get_user_model()


class DRFTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION')
        if not auth:
            raise exceptions.AuthenticationFailed('Missing authorization header')
        auth = auth.split()
        if len(auth) != 2 or auth[0] != 'Token':
            raise exceptions.AuthenticationFailed('Invalid authorization header')
        token = auth[1]

        if token:
            try:
                user = User.objects.get(key=token)
                if user.is_active:
                    return user, None
                return None
            except User.DoesNotExist:
                return None
