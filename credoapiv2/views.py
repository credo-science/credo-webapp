# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

from credocommon.exceptions import RegistrationException

from credoapiv2.authentication import DRFTokenAuthentication
from credoapiv2.exceptions import CredoAPIException, LoginException
from credoapiv2.handlers import handle_registration, handle_login, handle_detection, handle_update_info, handle_ping, \
    handle_data_export, handle_mapping_export

import logging

logger = logging.getLogger(__name__)


class UserRegistrationView(APIView):
    """
    post:
    Register user
    """
    parser_classes = (JSONParser,)

    def post(self, request):
        try:
            handle_registration(request)
            return Response(status=status.HTTP_200_OK, data={'message': 'Please check your email for activation link.'})
        except RegistrationException as e:
            return Response(data={'message': 'Registration failed. Reason: ' + str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except CredoAPIException as e:
            return Response(data={'message':  e},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(e)
            raise e


class UserLoginView(APIView):
    """
    post:
    Login user
    """
    parser_classes = (JSONParser,)
    throttle_scope = 'api_v2_login'

    def post(self, request, format=None):
        try:
            return Response(data=handle_login(request), status=status.HTTP_200_OK)
        except LoginException as e:
            return Response(data={'message': 'Login failed. Reason: ' + str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except CredoAPIException as e:
            return Response(data={'message':  e},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(e)
            raise e


class UserInfoView(APIView):
    """
    post:
    Change information about user
    """
    authentication_classes = (DRFTokenAuthentication, )
    parser_classes = (JSONParser,)

    def post(self, request):
        if request.user.is_authenticated:
            try:
                data = handle_update_info(request)
                return Response(data=data, status=status.HTTP_200_OK)
            except CredoAPIException as e:
                return Response(data={'message': 'Updating user info failed. Reason: ' + str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.exception(e)
                raise e
        else:
            return Response(data={'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


class DetectionView(APIView):
    """
    post:
    Submit detection
    """
    authentication_classes = (DRFTokenAuthentication, )
    parser_classes = (JSONParser,)

    def post(self, request):
        if request.user.is_authenticated:
            try:
                data = handle_detection(request)
                return Response(data=data, status=status.HTTP_200_OK)
            except CredoAPIException as e:
                return Response(data={'message': 'Submitting detection failed. Reason: ' + str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.exception(e)
                raise e
        else:
            return Response(data={'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


class PingView(APIView):
    """
    post:
    Submit ping
    """
    authentication_classes = (DRFTokenAuthentication, )
    parser_classes = (JSONParser,)

    def post(self, request):
        if request.user.is_authenticated:
            try:
                handle_ping(request)
                return Response(status=status.HTTP_200_OK)
            except CredoAPIException as e:
                return Response(data={'message': 'Ping failed. Reason: ' + str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.exception(e)
                raise e
        else:
            return Response(data={'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


class DataExportView(APIView):
    """
    post:
    Export data
    """
    authentication_classes = (DRFTokenAuthentication, )
    parser_classes = (JSONParser,)
    throttle_scope = 'data_export'

    def post(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            try:
                return Response(data=handle_data_export(request), status=status.HTTP_200_OK)
            except CredoAPIException as e:
                return Response(data={'message': 'Data export failed. Reason: ' + str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.exception(e)
                raise e
        else:
            return Response(data={'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


class MappingExportView(APIView):
    """
    post:
    Export mapping
    """
    authentication_classes = (DRFTokenAuthentication, )
    parser_classes = (JSONParser,)
    throttle_scope = 'data_export'

    def post(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            try:
                return Response(data=handle_mapping_export(request), status=status.HTTP_200_OK)
            except CredoAPIException as e:
                return Response(data={'message': 'Mapping export failed. Reason: ' + str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.exception(e)
                raise e
        else:
            return Response(data={'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
