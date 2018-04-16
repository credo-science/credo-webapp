from django.contrib.auth import get_user_model
User = get_user_model()

"""
Authentication example:

from django.contrib.auth import authenticate

user = authenticate(None, token='aaaa01')
"""


class TokenBackend(object):
    @staticmethod
    def authenticate(_, token=None):
        try:
            return User.objects.get(key=token)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
