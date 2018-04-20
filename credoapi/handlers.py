from credoapi.helpers import OutputFrame, OutputHeader, Body, UserInfo, generate_key
from credoapi.serializers import OutputFrameSerializer, UserInfoSerializer
from credoapi.models import User, Team, Device, Detection
from credoapi.exceptions import RegisterException, LoginException

from django.db.utils import IntegrityError
from django.core.mail import send_mail
from django.contrib.auth import authenticate

import logging

logger = logging.getLogger(__name__)


def handle_register_frame(frame):
    # throw proper exception on duplicated user
    user_info = frame['body']['user_info']
    # device_info = frame['body']['device_info']

    # create or get team
    team_name = user_info['team']
    team, _ = Team.objects.get_or_create(name=team_name)

    # create user
    user_email = user_info['email']
    user_name = user_info['name']

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
    key = frame['body']['key_info']['key']

    user = authenticate(token=key)

    if user == None:
        logger.info("Unsuccessful login attempt." % user.display_name)
        raise LoginException("Wrong username or password!")

    logger.info("User %s logged in." % user.display_name)

    user_info = UserInfoSerializer(user)
    body = Body(user_info=user_info)
    output_header = OutputHeader('server', 'login', '1.3')
    output_frame = OutputFrame(output_header, body)
    output_frame_serializer = OutputFrameSerializer(output_frame)
    return output_frame_serializer.data


def handle_ping_frame(frame):
    pass


def handle_detection_frame(frame):
    pass
