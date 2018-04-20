# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64

from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from credoapi.backends import TokenBackend

from credoapi.models import User, Detection, Device


class ManageUser(APIView):
    def post(self, request, format=None):
        return Response(data={'request_data': request.data})


class ManageDetection(APIView):
    authentication_classes = (TokenBackend, )
    parser_classes = (JSONParser,)

    def post(self, request, format=None):
        if request.user.is_authenticated:
            Detection.objects.create(
                accuracy=request.data['accuracy'],
                altitude=request.data['altitude'],
                frame_content=base64.b64decode(request.data['frame_content']),
                height=request.data['height'],
                width=request.data['height'],
                d_id=request.data['id'],
                latitude=request.data['latitude'],
                longitude=request.data['longitude'],
                provider=request.data['provider'],
                timestamp=request.data['timestamp'],
                device=Device.objects.get_or_create(
                    device_id=request.data['device_id'],
                    device_model=request.data['device_model'],
                    android_version=request.data['android_version'],
                    user=request.user
                )[0],
                user=request.user
            )
            data = {
                'user': request.user.username,
                'message': 'OK',
            }
            return Response(data=data)
        else:
            return Response()
