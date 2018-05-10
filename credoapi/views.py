# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from credoapi.serializers import InputFrameSerializer, ErrorSerializer
from credoapi.helpers import Error
from credoapi.negotiation import IgnoreClientContentNegotiation
from credoapi.handlers import handle_detection_frame, handle_login_frame, handle_ping_frame, handle_register_frame
from credoapi.exceptions import RegisterException, LoginException, UnauthorizedException

from django.shortcuts import render
from django.http import HttpResponseRedirect

import logging

logger = logging.getLogger(__name__)


class InputFrameHandler(APIView):
    content_negotiation_class = IgnoreClientContentNegotiation

    def get(self, request, format=None):
        return HttpResponseRedirect('/web/')

    def wrap_error(self, err, message):
        error = Error(err, message)
        error_serializer = ErrorSerializer(error)
        return error_serializer.data

    def post(self, request, format=None):
        if len(request.data) == 0:
            # doesn't look like api request, redirect to /web/
            return HttpResponseRedirect('/web/')

        serializer = InputFrameSerializer(data=request.data)
        if serializer.is_valid():
            frame = serializer.save()
            frame_type = frame.header.frame_type

            try:
                response = None

                if frame_type == 'detection':
                    handle_detection_frame(frame)
                elif frame_type == 'login':
                    response = handle_login_frame(frame)
                elif frame_type == 'ping':
                    handle_ping_frame(frame)
                elif frame_type == 'register':
                    handle_register_frame(frame)

                return Response(response, status=status.HTTP_200_OK)
            except RegisterException as e:
                return Response(self.wrap_error('Registration problem', str(e)),
                                status=status.HTTP_400_BAD_REQUEST)
            except LoginException as e:
                return Response(self.wrap_error('Login problem', str(e)),
                                status=status.HTTP_401_UNAUTHORIZED)
            except UnauthorizedException as e:
                return Response(self.wrap_error('Unauthorized', str(e)),
                                status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                logging.exception("Error processing request")
                return Response(self.wrap_error('internal server error', str(e)),
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # TODO: add logging here

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
