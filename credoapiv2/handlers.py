# -*- coding: utf-8 -*-
import base64
import hashlib

import boto3
import requests

from redis.exceptions import LockNotOwnedError

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.db.utils import IntegrityError
from django_redis import get_redis_connection
from rest_framework.exceptions import ParseError

from credocommon.helpers import (
    generate_token,
    validate_image,
    register_user,
    register_oauth_user,
)
from credocommon.jobs import (
    data_export,
    recalculate_user_stats,
    recalculate_team_stats,
    mapping_export,
)
from credocommon.models import get_default_team, User, Team, Detection, Device, Ping

from credocommon.oauth import get_token, get_userinfo

from credoapiv2.exceptions import CredoAPIException, LoginException
from credoapiv2.serializers import (
    RegisterRequestSerializer,
    LoginRequestSerializer,
    OAuthLoginRequestSerializer,
    InfoRequestSerializer,
    DetectionRequestSerializer,
    PingRequestSerializer,
    DataExportRequestSerializer,
    MappingExportRequestSerializer,
)

import logging

logger = logging.getLogger(__name__)


def handle_registration(request):
    try:
        serializer = RegisterRequestSerializer(data=request.data)
    except ParseError:
        raise CredoAPIException("Could not parse request body as a valid JSON object")

    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data

    register_user(
        vd["email"], vd["password"], vd["username"], vd["display_name"], vd["team"]
    )


def handle_login(request):
    try:
        serializer = LoginRequestSerializer(data=request.data)
    except ParseError:
        raise CredoAPIException("Could not parse request body as a valid JSON object")

    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data

    if vd.get("username"):
        user = authenticate(username=vd["username"], password=vd["password"])
    elif request.data.get("email"):
        user = authenticate(email=vd["email"], password=vd["password"])
    else:
        raise LoginException("Missing credentials.")
    if not user:
        raise LoginException(
            "Invalid username/email and password combination or unverified email."
        )
    if not user.is_active:
        raise LoginException("Email not verified.")

    data = {
        "username": user.username,
        "display_name": user.display_name,
        "email": user.email,
        "team": user.team.name,
        "language": user.language,
        "token": user.key,
    }
    logger.info("Logging in user {}".format(user))
    return data


def handle_oauth_login(request):
    try:
        serializer = OAuthLoginRequestSerializer(data=request.data)
    except ParseError:
        raise CredoAPIException("Could not parse request body as a valid JSON object")

    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data

    try:
        oat, _ = get_token(vd["authorization_code"], vd["provider"])
    except requests.exceptions.RequestException as e:
        raise CredoAPIException(str(e))

    try:
        email, username, display_name = get_userinfo(oat, vd["provider"])
    except requests.exceptions.RequestException as e:
        raise CredoAPIException(str(e))

    new_account = False

    try:
        user = User.objects.get(email=email)
        if not user.is_active:
            logger.info("Enabling user account because of valid OAuth login")
            user.is_active = True
            user.save()
    except User.DoesNotExist:
        user = register_oauth_user(email, username, display_name, vd["provider"])
        new_account = True

    data = {
        "new_account": new_account,
        "token": user.key,
    }

    logger.info("OAuth login for user {}".format(user))
    return data


def handle_update_info(request):
    try:
        serializer = InfoRequestSerializer(data=request.data)
    except ParseError:
        raise CredoAPIException("Could not parse request body as a valid JSON object")

    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data

    user = request.user
    update_fields = []

    if vd.get("display_name"):
        user.display_name = vd["display_name"]
        update_fields.append("display_name")

    if vd.get("team") is not None:
        user.team = Team.objects.get_or_create(name=vd["team"])[0]
        update_fields.append("team")

    if vd.get("language"):
        user.language = vd["language"]
        update_fields.append("language")

    try:
        user.save(update_fields=update_fields)
        logger.info("Updated info for user {}".format(user))
    except IntegrityError:
        raise CredoAPIException("Invalid parameters")

    data = {
        "username": user.username,
        "display_name": user.display_name,
        "email": user.email,
        "team": user.team.name,
        "language": user.language,
    }
    return data


def handle_user_delete_account(request):
    u = request.user

    rnd_name = "deleted_" + generate_token()[:16]
    u.username = rnd_name
    u.display_name = rnd_name
    u.email = rnd_name + "@notvalid.credo.science"

    u.team = get_default_team()

    u.key = generate_token()
    u.generate_token()
    u.email_confirmation_token = generate_token()
    u.set_password(generate_token())

    u.is_active = False
    u.is_staff = False

    u.save()

    data = {"success": True}
    return data


def handle_user_id(request):
    data = {
        "id": hashlib.sha3_256(
            "credo_user-{}".format(request.user.id).encode()
        ).hexdigest()
    }
    return data


def handle_detection(request):
    try:
        serializer = DetectionRequestSerializer(data=request.data)
    except ParseError:
        raise CredoAPIException("Could not parse request body as a valid JSON object")

    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data
    detections = []

    try:
        with cache.lock("lock_user-{}".format(request.user.id), timeout=10):
            logger.info("acquired lock for user {}".format(request.user.id))
            r = None
            for d in vd["detections"]:

                frame_content = base64.b64decode(d["frame_content"])
                visible = True
                if (not frame_content) or (not validate_image(frame_content)):
                    visible = False

                if visible:
                    if not r:
                        r = get_redis_connection(write=False)
                    start_time = r.zscore(cache.make_key("start_time"), request.user.id)
                    if start_time:
                        visible = d["timestamp"] > start_time
                    else:
                        visible = False

                if visible and d["x"] is not None:
                    r = get_redis_connection()
                    if not r.sadd(
                        cache.make_key("pixels_{}".format(request.user.id)),
                        "{} {}".format(d["x"], d["y"]),
                    ):
                        visible = False

                detections.append(
                    Detection.objects.create(
                        accuracy=d["accuracy"],
                        altitude=d["altitude"],
                        frame_content=frame_content,
                        height=d["height"],
                        width=d["width"],
                        x=d["x"],
                        y=d["y"],
                        latitude=d["latitude"],
                        longitude=d["longitude"],
                        provider=d["provider"],
                        timestamp=d["timestamp"],
                        metadata=d["metadata"],
                        source="api_v2",
                        device=Device.objects.get_or_create(
                            device_id=vd["device_id"],
                            device_type=vd["device_type"],
                            device_model=vd["device_model"],
                            system_version=vd["system_version"],
                            user=request.user,
                        )[0],
                        user=request.user,
                        team=request.user.team,
                        visible=visible,
                    )
                )
    except LockNotOwnedError:
        logger.info("could not release lock for user {}".format(request.user.id))
    data = {"detections": [{"id": d.id} for d in detections]}
    recalculate_user_stats.delay(request.user.id)
    recalculate_team_stats.delay(request.user.team.id)
    logger.info(
        "Stored {} detections for user {}".format(len(detections), request.user)
    )
    return data


def handle_ping(request):
    try:
        serializer = PingRequestSerializer(data=request.data)
    except ParseError:
        raise CredoAPIException("Could not parse request body as a valid JSON object")

    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))

    vd = serializer.validated_data

    try:
        with cache.lock("lock_user-{}".format(request.user.id), timeout=10):
            logger.info("acquired lock for user {}".format(request.user.id))
            Ping.objects.create(
                timestamp=vd["timestamp"],
                delta_time=vd["delta_time"],
                on_time=vd["on_time"],
                metadata=vd["metadata"],
                device=Device.objects.get_or_create(
                    device_id=vd["device_id"],
                    device_type=vd["device_type"],
                    device_model=vd["device_model"],
                    system_version=vd["system_version"],
                    user=request.user,
                )[0],
                user=request.user,
            )

            if vd["on_time"]:
                recalculate_user_stats.delay(request.user.id)
    except LockNotOwnedError:
        logger.info("could not release lock for user {}".format(request.user.id))
    logger.info("Stored ping for user {}".format(request.user))


def handle_data_export(request):
    try:
        serializer = DataExportRequestSerializer(data=request.data)
    except ParseError:
        raise CredoAPIException("Could not parse request body as a valid JSON object")

    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))

    vd = serializer.validated_data

    job_id = generate_token()[:16]

    s3 = boto3.resource(
        "s3",
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_ENDPOINT_URL,
    )

    url = s3.meta.client.generate_presigned_url(
        ClientMethod="get_object",
        ExpiresIn=settings.S3_EXPIRES_IN,
        Params={"Bucket": settings.S3_BUCKET, "Key": "export_{}.json".format(job_id)},
    )

    data_export.delay(job_id, vd["since"], vd["until"], vd["limit"], vd["data_type"])

    logger.info(
        "Exporting data by request from {}, type {}, since {}, until {}, limit {}, id {}".format(
            request.user, vd["data_type"], vd["since"], vd["until"], vd["limit"], job_id
        )
    )
    return {"url": url}


def handle_mapping_export(request):
    try:
        serializer = MappingExportRequestSerializer(data=request.data)
    except ParseError:
        raise CredoAPIException("Could not parse request body as a valid JSON object")

    if not serializer.is_valid():
        raise CredoAPIException(str(serializer.errors))
    vd = serializer.validated_data

    job_id = generate_token()[:16]

    s3 = boto3.resource(
        "s3",
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_ENDPOINT_URL,
    )

    url = s3.meta.client.generate_presigned_url(
        ClientMethod="get_object",
        ExpiresIn=settings.S3_EXPIRES_IN,
        Params={
            "Bucket": settings.S3_BUCKET,
            "Key": "mapping_export_{}.json".format(job_id),
        },
    )

    mapping_export.delay(job_id, vd["mapping_type"])

    logger.info(
        "Exporting mapping by request from {}, type {}, id {}".format(
            request.user, vd["mapping_type"], job_id
        )
    )

    return {"url": url}
