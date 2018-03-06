# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from credoapi.models import Team, User, Device, Detection
from credoapi.serializers import DetectionSerializer

from django.shortcuts import render


@api_view(['POST'])
def handle_detection(request):
    serializer = DetectionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response("", status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
