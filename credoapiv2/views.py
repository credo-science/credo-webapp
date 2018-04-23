# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

from credoapiv2.authentication import DRFTokenAuthentication
from credoapiv2.handlers import handle_detection


class ManageUserRegistration(APIView):
    def post(self, request, format=None):
        return Response(data={'request_data': request.data})


class ManageDetection(APIView):
    """
    post:
    Submit detection
    """
    authentication_classes = (DRFTokenAuthentication, )
    parser_classes = (JSONParser,)

    def post(self, request, format=None):
        if request.user.is_authenticated:
            handle_detection(request)
            data = {
                'user': request.user.username,
                'message': 'OK',
            }
            return Response(data=data)
        else:
            return Response(data={'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
