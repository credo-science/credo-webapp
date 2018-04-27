# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

from credoapiv2.authentication import DRFTokenAuthentication
from credoapiv2.exceptions import CredoAPIException, RegistrationException, LoginException
from credoapiv2.handlers import handle_registration, handle_login, handle_detection, handle_update_info, handle_ping

import logging

logger = logging.getLogger(__name__)


class ManageUserRegistration(APIView):
    """
    post:
    Register user
    """
    parser_classes = (JSONParser,)

    def post(self, request, format=None):
        try:
            handle_registration(request)
            return Response(status=status.HTTP_200_OK)
        except RegistrationException as e:
            return Response(data={'message': 'Registration failed. Reason: ' + e.message},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ManageUserLogin(APIView):
    """
    post:
    Login user
    """
    parser_classes = (JSONParser,)

    def post(self, request, format=None):
        try:
            return Response(data=handle_login(request), status=status.HTTP_200_OK)
        except LoginException as e:
            return Response(data={'message': 'Login failed. Reason: ' + e.message},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ManageUserInfo(APIView):
    """
    post:
    Change information about user
    """
    authentication_classes = (DRFTokenAuthentication, )
    parser_classes = (JSONParser,)

    def post(self, request, format=None):
        if request.user.is_authenticated:
            try:
                data = handle_update_info(request)
                return Response(data=data, status=status.HTTP_200_OK)
            except CredoAPIException as e:
                return Response(data={'message': 'Updating user info failed. Reason: ' + e.message},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.exception(e)
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data={'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


class ManageDetection(APIView):
    """
    post:
    Submit detection
    """
    authentication_classes = (DRFTokenAuthentication, )
    parser_classes = (JSONParser,)

    def post(self, request, format=None):
        if request.user.is_authenticated:
            try:
                data = handle_detection(request)
                return Response(data=data, status=status.HTTP_200_OK)
            except CredoAPIException as e:
                return Response(data={'message': 'Submitting detection failed. Reason: ' + e.message},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.exception(e)
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data={'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


class ManagePing(APIView):
    """
    post:
    Submit ping
    """
    authentication_classes = (DRFTokenAuthentication, )
    parser_classes = (JSONParser,)

    def post(self, request, format=None):
        if request.user.is_authenticated:
            try:
                handle_ping(request)
                return Response(status=status.HTTP_200_OK)
            except CredoAPIException as e:
                return Response(data={'message': 'Ping failed. Reason: ' + e.message},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.exception(e)
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data={'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
