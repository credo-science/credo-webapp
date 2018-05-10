from credoapi.helpers import OutputFrame, OutputHeader, OutputBody, UserInfo, generate_key
from credoapi.serializers import OutputFrameSerializer
from credocommon.models import User, Team, Device, Detection, Ping
from credoapi.exceptions import RegisterException, LoginException, UnauthorizedException

from django.db.utils import IntegrityError
from django.core.mail import send_mail
from django.contrib.auth import authenticate

import logging
import time

logger = logging.getLogger(__name__)


def handle_register_frame(frame):
    user_info = frame.body.user_info

    # create or get team
    team_name = user_info.team
    team, _ = Team.objects.get_or_create(name=team_name)

    # create user
    user_email = user_info.email
    user_name = user_info.name

    key = generate_key()
    while User.objects.filter(key=key).exists():
        key = generate_key()

    try:
        user = User.objects.create_user(
            team=team,
            display_name=user_name,
            key=key,
            password=key,
            username=user_name,
            email=user_email
        )

        device_info = frame.body.device_info

        device, _ = Device.objects.get_or_create(
            device_id=device_info.deviceId,
            device_model=device_info.deviceModel,
            system_version=device_info.androidVersion,
            user=user
        )

    except IntegrityError as e:
        if 'UNIQUE' in e.message:
            logger.info("Already registered user tried to register! {%s, %s}" % (user_name, user_email))
            raise RegisterException("Username or e-mail address is already registered!")
        else:
            raise e

    # send email with key
    send_mail(
        "Credo API registration information",
        "Hello!\n\nThank you for registering in Credo API Portal, your generated access token is: %s please use it for login operation in the mobile app. \n\nbest regards,\nCredo Team" % key,
        'credoapi@credo.science',
        [user_email],
        fail_silently=False
    )

    logger.info("Registered new user {%s, %s}" % (user_name, user_email))

    return


def handle_login_frame(frame):
    key = frame.body.key_info.key

    user = authenticate(token=key)

    if user is None:
        logger.info("Unsuccessful login attempt.")
        raise LoginException("Wrong username or password!")

    device_info = frame.body.device_info

    device, _ = Device.objects.get_or_create(
        device_id=device_info.deviceId,
        device_model=device_info.deviceModel,
        system_version=device_info.androidVersion,
        user=user
    )

    logger.info("User %s logged in." % user.display_name)

    user_info = UserInfo(team=user.team.name, email=user.email, name=user.display_name, key=user.key)
    body = OutputBody(user_info=user_info)
    output_header = OutputHeader('2.0', 'login', '1.0')
    output_frame = OutputFrame(output_header, body)
    output_frame_serializer = OutputFrameSerializer(output_frame)
    return output_frame_serializer.data


def handle_ping_frame(frame):
    key = frame.body.user_info.key

    user = authenticate(token=key)

    if user is None:
        logger.info("Unauthorized ping.")
        raise UnauthorizedException("Wrong username or password!")

    device_info = frame.body.device_info

    device, _ = Device.objects.get_or_create(
        device_id=device_info.deviceId,
        device_model=device_info.deviceModel,
        system_version=device_info.androidVersion,
        user=user
    )

    ping = Ping.objects.create(
        timestamp=int(time.time() * 1000),
        user=user,
        device=device
    )

    logger.info("Stored ping for user %s." % user.display_name)


def handle_detection_frame(frame):
    key = frame.body.user_info.key
    user_info = frame.body.user_info

    user = authenticate(token=key)

    # create or get team
    team_name = user_info.team
    team, _ = Team.objects.get_or_create(name=team_name)

    if not team == user.team:
        user.team = team
        user.save()

    if user is None:
        logger.info("Unauthorized detection submission.")
        raise UnauthorizedException("Wrong username or password!")

    device_info = frame.body.device_info

    device, _ = Device.objects.get_or_create(
        device_id=device_info.deviceId,
        device_model=device_info.deviceModel,
        system_version=device_info.androidVersion,
        user=user
    )

    detection_info = frame.body.detection_info
    detection = Detection.objects.create(
        accuracy=detection_info.accuracy,
        altitude=detection_info.altitude,
        frame_content=detection_info.frame_content,
        height=detection_info.height,
        width=detection_info.width,
        d_id=detection_info.id,
        latitude=detection_info.latitude,
        longitude=detection_info.longitude,
        provider=detection_info.provider,
        timestamp=detection_info.timestamp,
        source='api_v1',
        device=device,
        user=user,
        team = user.team
    )

    logger.info("Stored detection for user %s." % user.display_name)
