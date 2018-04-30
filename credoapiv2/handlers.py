# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64

from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.db.utils import IntegrityError

from credoapi.helpers import generate_token
from credoapi.models import User, Team, Detection, Device, Ping

from credoapiv2.exceptions import CredoAPIException, RegistrationException, LoginException
from credoapiv2.serializers import RegisterRequestSerializer


def handle_registration(request):
    serializer = RegisterRequestSerializer(data=request.data)
    if not serializer.is_valid():
        raise CredoAPIException(serializer.errors)
    data = serializer.validated_data
    try:
        key = generate_token()
        email_confirmation_token = generate_token()
        user = User.objects.create_user(
            team=Team.objects.get_or_create(name=data['team'])[0],
            display_name=data['display_name'],
            key=key,
            password=data['password'],
            username=data['username'],
            email=data['email'],
            is_active=False,
            email_confirmation_token=email_confirmation_token,
        )
        if user:
            send_mail(
                'Credo API registration information',
                'Hello!\n\nThank you for registering in Credo API Portal, '
                'please confirm your email by visiting the link below:\n\n  '
                '<a href="https://credo.science/web/confirm_email/{token}">https://credo.science/web/confirm_email/{token}</a> %s \n\n'
                'best regards,\nCredo Team'.format(token=email_confirmation_token),
                'credoapi@credo.science',
                [user.email],
            )
    except IntegrityError:
        raise RegistrationException("User with given username or email already exists.")


def handle_login(request):
    if request.data.get('username'):
        user = authenticate(username=request.data['username'], password=request.data['password'])
    elif request.data.get('email'):
        user = authenticate(username=request.data['email'], password=request.data['password'])
    else:
        raise LoginException('Missing credentials.')
    if not user:
        raise LoginException('Invalid username/email and password combination or unverified email.')
    if not user.is_active:
        raise LoginException('Email not verified.')

    data = {
        'username': user.username,
        'display_dame': user.display_name,
        'email': user.email,
        'team': user.team.name,
        'language': user.language,
        'token': user.key
    }
    return data


def handle_update_info(request):
    user = request.user
    update_fields = []

    if request.data.get('display_name'):
        user.display_name = request.data.get('display_name')
        update_fields.append('display_name')

    if request.data.get('team'):
        user.team = Team.objects.get_or_create(name=request.data['team'])
        update_fields.append('team')

    if request.data.get('language'):
        user.language = request.data.get('language')
        update_fields.append('language')

    try:
        user.save(update_fields=update_fields)
    except IntegrityError:
        raise CredoAPIException('Invalid parameters')

    data = {
        'username': user.username,
        'display_dame': user.display_name,
        'email': user.email,
        'team': user.team.name,
        'language': user.language,
    }
    return data


def handle_detection(request):
    data = {
        'ids': []
    }
    for d in request.data['detections']:
        data['ids'].append(Detection.objects.create(
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
            device=Device.objects.get_or_create(
                device_id=request.data['device_id'],
                device_type=request.data['device_type'],
                device_model=request.data['device_model'],
                system_version=request.data['system_version'],
                user=request.user
            )[0],
            user=request.user,
            team=request.user.team
        ).pk)
    return data


def handle_ping(request):
    Ping.objects.create(
        timestamp=request.data['timestamp'],
        delta_time=request.data['delta_time'],
        device=Device.objects.get_or_create(
            device_id=request.data['device_id'],
            device_model=request.data['device_model'],
            system_version=request.data['system_version'],
            user=request.user
        )[0],
        user=request.user
    )
