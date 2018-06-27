# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64

import boto3

from django.conf import settings
from django.contrib.auth import authenticate
from django.db.utils import IntegrityError

from credocommon.helpers import generate_token, validate_image, register_user, rate_brightness
from credocommon.jobs import data_export, recalculate_on_time
from credocommon.models import User, Team, Detection, Device, Ping

from credoapiv2.exceptions import CredoAPIException, LoginException
from credoapiv2.serializers import RegisterRequestSerializer, LoginRequestSerializer, InfoRequestSerializer, \
    DetectionRequestSerializer, PingRequestSerializer, DataExportRequestSerializer

import logging

logger = logging.getLogger(__name__)


def handle_registration(request):
    serializer = RegisterRequestSerializer(data=request.data)
    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data
    register_user(vd['email'], vd['password'], vd['username'], vd['display_name'], vd['team'])


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
        if (not frame_content) or (not validate_image(frame_content)):
            visible = False

        brightness = None

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
            visible=visible,
            brightness=brightness
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

    if vd['on_time']:
        recalculate_on_time.delay(request.user.id)

    logger.info('Stored ping for user {}'.format(request.user))


def handle_data_export(request):
    serializer = DataExportRequestSerializer(data=request.data)
    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data

    job_id = generate_token()[:16]

    s3 = boto3.resource(
        's3',
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_ENDPOINT_URL
    )

    url = s3.meta.client.generate_presigned_url(
        ClientMethod='get_object',
        ExpiresIn=settings.S3_EXPIRES_IN,
        Params={
            'Bucket': settings.S3_BUCKET,
            'Key': 'export_{}.json'.format(job_id)
        }
    )

    data_export.delay(job_id, vd['since'], vd['until'], vd['limit'], vd['data_type'])

    logger.info('Exporting data by request from {}, type {}, since {}, until {}, limit {}, id {}'
                .format(request.user, vd['data_type'], vd['since'], vd['until'], vd['limit'], job_id))
    return {
        'url': url
    }
