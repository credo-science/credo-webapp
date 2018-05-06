# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64

from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.db.utils import IntegrityError

from credocommon.models import User, Team, Detection, Device, Ping
from credocommon.helpers import generate_token

from credoapiv2.exceptions import CredoAPIException, RegistrationException, LoginException
from credoapiv2.serializers import RegisterRequestSerializer, LoginRequestSerializer, InfoRequestSerializer,\
    DetectionRequestSerializer, PingRequestSerializer


def handle_registration(request):
    serializer = RegisterRequestSerializer(data=request.data)
    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data

    try:
        user = User.objects.create_user(
            team=Team.objects.get_or_create(name=vd['team'])[0],
            display_name=vd['display_name'],
            key=generate_token(),
            password=vd['password'],
            username=vd['username'],
            email=vd['email'],
            is_active=False,
            email_confirmation_token=generate_token(),
        )
        if user:
            send_mail(
                'Credo API registration information',
                'Hello!\n\nThank you for registering in Credo API Portal, '
                'please confirm your email by visiting the link below:\n\n  '
                '<a href="https://credo.science/web/confirm_email/{token}">https://credo.science/web/confirm_email/{token}</a> %s \n\n'
                'best regards,\nCredo Team'.format(token=user.email_confirmation_token),
                'credoapi@credo.science',
                [user.email],
            )
    except IntegrityError:
        raise RegistrationException("User with given username or email already exists.")


def handle_login(request):
    serializer = LoginRequestSerializer(data=request.data)
    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data

    if vd.get('username'):
        user = authenticate(username=vd['username'], password=vd['password'])
    elif request.data.get('email'):
        user = authenticate(email=vd['email'], password=vd['password'])
    else:
        raise LoginException('Missing credentials.')
    if not user:
        raise LoginException('Invalid username/email and password combination or unverified email.')
    if not user.is_active:
        raise LoginException('Email not verified.')

    data = {
        'username': user.username,
        'display_name': user.display_name,
        'email': user.email,
        'team': user.team.name,
        'language': user.language,
        'token': user.key
    }
    return data


def handle_update_info(request):
    serializer = InfoRequestSerializer(data=request.data)
    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data

    user = request.user
    update_fields = []

    if vd.get('display_name'):
        user.display_name = vd['display_name']
        update_fields.append('display_name')

    if vd.get('team') is not None:
        user.team = Team.objects.get_or_create(name=vd['team'])[0]
        update_fields.append('team')

    if vd.get('language'):
        user.language = vd['language']
        update_fields.append('language')

    try:
        user.save(update_fields=update_fields)
    except IntegrityError:
        raise CredoAPIException('Invalid parameters')

    data = {
        'username': user.username,
        'display_name': user.display_name,
        'email': user.email,
        'team': user.team.name,
        'language': user.language,
    }
    return data


def handle_detection(request):
    serializer = DetectionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data
    detections = []
    for d in vd['detections']:
        detections.append(Detection.objects.create(
            accuracy=d['accuracy'],
            altitude=d['altitude'],
            frame_content=base64.b64decode(d['frame_content']),
            height=d['height'],
            width=d['height'],
            d_id=d['id'],
            latitude=d['latitude'],
            longitude=d['longitude'],
            provider=d['provider'],
            timestamp=d['timestamp'],
            source='api_v2',
            device=Device.objects.get_or_create(
                device_id=vd['device_id'],
                device_type=vd['device_type'],
                device_model=vd['device_model'],
                system_version=vd['system_version'],
                user=request.user
            )[0],
            user=request.user,
            team=request.user.team
        ))
    data = {
        'detections': [{
            'id': d.id  # TODO: Should we send more data?
        } for d in detections]
    }

    return data


def handle_ping(request):
    serializer = PingRequestSerializer(data=request.data)
    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data
    Ping.objects.create(
        timestamp=vd['timestamp'],
        delta_time=vd['delta_time'],
        device=Device.objects.get_or_create(
            device_id=vd['device_id'],
            device_type=vd['device_type'],
            device_model=vd['device_model'],
            system_version=vd['system_version'],
            user=request.user
        )[0],
        user=request.user
    )
