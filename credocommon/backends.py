from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(object):
    @staticmethod
    def authenticate(email=None, password=None):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(password) and user.is_active:
                return user
        return None
