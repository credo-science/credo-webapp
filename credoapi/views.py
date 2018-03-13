# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from credoapi.models import Team, User, Device, Detection
from credoapi.serializers import FrameSerializer

from django.shortcuts import render


@api_view(['POST'])
def handle_frame(request):
    # print request.data
    serializer = FrameSerializer(data=request.data)
    if serializer.is_valid():
        # serializer.save()
        return Response("", status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
