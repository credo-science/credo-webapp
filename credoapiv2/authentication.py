# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model

from rest_framework import authentication
from rest_framework import exceptions

import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class DRFTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION")
        if not auth:
            raise exceptions.AuthenticationFailed("Missing authorization header")
        auth = auth.split()
        if len(auth) != 2 or auth[0] != "Token":
            raise exceptions.AuthenticationFailed("Invalid authorization header")
        token = auth[1]

        if token:
            try:
                user = User.objects.get(key=token)
                if user.is_active:
                    logger.info("Authenticated user {}".format(user))
                    return user, None
                return None
            except User.DoesNotExist:
                logger.info("Failed authentication for token {}".format(token))
                return None
