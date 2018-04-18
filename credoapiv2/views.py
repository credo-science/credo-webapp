# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response

from credoapi.models import User


class ManageUser(APIView):
    def post(self, request, format=None):
        return Response(data={'request_data': request.data})


class ManageDetection(APIView):
    def post(self, request, format=None):
        return Response(data={'request_data': request.data})
