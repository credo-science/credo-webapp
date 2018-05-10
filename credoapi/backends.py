# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
User = get_user_model()

"""
Authentication example:

from django.contrib.auth import authenticate

user = authenticate(token='aaaa01')
"""


class TokenBackend(object):
    @staticmethod
    def authenticate(token=None):
        if token:
            try:
                user = User.objects.get(key=token)
                if user.is_active:
                    return user
                return None
            except User.DoesNotExist:
                return None

    @staticmethod
    def get_user(username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
