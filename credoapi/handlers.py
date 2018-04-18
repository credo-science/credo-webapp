from credoapi.helpers import OutputFrame, OutputHeader, Body, UserInfo
from credoapi.serializers import OutputFrameSerializer
from credoapi.models import User, Team, Device, Detection

from django.db.utils import IntegrityError
from django.core.mail import send_mail

import string
from random import choice

CHARS = string.ascii_letters


def generate_key():
    return ''.join(choice(CHARS) for x in range(8))


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
        user = User.objects.create(
            team=team,
            display_name=user_name,
            key=key,
            username=user_name,
            email=user_email
        )
        user.set_password(key)
        user.save()
    except IntegrityError as e:
        if 'UNIQUE' in e.message:
            raise Exception("Username or e-mail address is already registered!")
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

    return


def handle_login_frame(frame):
    # user_info = UserInfo('myteam', 'email', 'name', 'key')
    # body = Body(user_info=user_info)
    # output_header = OutputHeader('server', 'login', '1.3', 123123123)
    # output_frame = OutputFrame(output_header, body)
    # output_frame_serializer = OutputFrameSerializer(output_frame)
    # return output_frame_serializer.data
    return ''


def handle_ping_frame(frame):
    pass


def handle_detection_frame(frame):
    pass
