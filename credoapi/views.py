# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from credoapi.models import Team, User, Device, Detection
from credoapi.serializers import FrameSerializer

from django.shortcuts import render
from django.http import HttpResponseRedirect

import json


@api_view(['GET'])
def handle_get_requests(request):
    return HttpResponseRedirect('/web/')


@api_view(['POST'])
def handle_frame(request):
    # print request.data
    try:
        json.loads(request.data)
    except ValueError, ve:
        # doesn't look like api request, redirect to /web/
        return HttpResponseRedirect('/web/')

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
