# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64

from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.db.utils import IntegrityError

from credocommon.models import User, Team, Detection, Device, Ping
from credocommon.helpers import generate_token, validate_image, send_registration_email

from credoapiv2.exceptions import CredoAPIException, RegistrationException, LoginException
from credoapiv2.serializers import RegisterRequestSerializer, LoginRequestSerializer, InfoRequestSerializer, \
    DetectionRequestSerializer, PingRequestSerializer, DataExportRequestSerializer, ExportDetectionSerializer, \
    ExportPingSerializer

import logging

logger = logging.getLogger(__name__)


def handle_registration(request):
    serializer = RegisterRequestSerializer(data=request.data)
    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data

    user = None

    try:
        u = User.objects.get(email=vd['email'])
        if not u.is_active:
            user = u
            user.team = Team.objects.get_or_create(name=vd['team'])[0]
            user.display_name = vd['display_name']
            user.key = generate_token()
            user.username = vd['username']
            user.email_confirmation_token = generate_token()
            user.set_password(vd['password'])
            user.save()
            logger.info('Updating user info and resending activation email to user {}'.format(user))
    except User.DoesNotExist:
        logger.info('Creating new user {} {}'.format(vd['username'], vd['display_name']))

    if not user:
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
        except IntegrityError:
            logger.warning('User registration failed, IntegrityError', vd)
            raise RegistrationException("User with given username or email already exists.")

    if user:
        logger.info('Sending registration email to {}'.format(user.email))
        try:
            send_registration_email(user.email, user.email_confirmation_token, user.username, user.display_name)
        except Exception as e:
            logger.exception(e)
            logger.error('Failed to send confirmation email for user {} ({})'.format(user, user.email))


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
    logger.info('Logging in user {}'.format(user))
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
        logger.info('Updated info for user {}'.format(user))
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

        frame_content = base64.b64decode(d['frame_content'])
        visible = True
        if (not frame_content) or validate_image(frame_content):
            visible = False

        detections.append(Detection.objects.create(
            accuracy=d['accuracy'],
            altitude=d['altitude'],
            frame_content=frame_content,
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
            team=request.user.team,
            visible=visible
        ))
    data = {
        'detections': [{
            'id': d.id  # TODO: Should we send more data?
        } for d in detections]
    }
    logger.info('Stored {} detections for user {}'.format(len(detections), request.user))
    return data


def handle_ping(request):
    serializer = PingRequestSerializer(data=request.data)
    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data
    Ping.objects.create(
        timestamp=vd['timestamp'],
        delta_time=vd['delta_time'],
        on_time=vd['on_time'],
        device=Device.objects.get_or_create(
            device_id=vd['device_id'],
            device_type=vd['device_type'],
            device_model=vd['device_model'],
            system_version=vd['system_version'],
            user=request.user
        )[0],
        user=request.user
    )
    logger.info('Stored ping for user {}'.format(request.user))


def handle_data_export(request):
    serializer = DataExportRequestSerializer(data=request.data)
    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data
    data = None
    if vd['data_type'] == 'detection':
        detections = Detection.objects.filter(time_received__gt=vd['since']).order_by('time_received')[:vd['limit']]
        data = {
            'detections': [ExportDetectionSerializer(d).data for d in detections]
        }
    elif vd['data_type'] == 'ping':
        pings = Ping.objects.filter(time_received__gt=vd['since']).order_by('time_received')[:vd['limit']]
        data = {
            'pings': [ExportPingSerializer(p).data for p in pings]
        }
    logger.info('Exporting data by request from {}, type {}, since {}, limit {}'.format(request.user, vd['data_type'],
                                                                                        vd['since'], vd['limit']))
    return data
