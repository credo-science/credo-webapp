# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from credoapi.models import Team, User, Device, Detection
from credoapi.serializers import FrameSerializer
from credoapi.negotiation import IgnoreClientContentNegotiation

from django.shortcuts import render
from django.http import HttpResponseRedirect

import json


class FrameHandler(APIView):
    content_negotiation_class = IgnoreClientContentNegotiation

    def get(self, request, format=None):
        return HttpResponseRedirect('/web/')

    def post(self, request, format=None):
        if len(request.data) == 0:
            # doesn't look like api request, redirect to /web/
            return HttpResponseRedirect('/web/')

        serializer = FrameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # print serializer.data
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print serializer.errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
