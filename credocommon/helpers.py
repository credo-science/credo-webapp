# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import io
import os

from PIL import Image, ImageStat

from django.core.mail import send_mail
from django.db import IntegrityError
from django.template.loader import render_to_string


import logging

logger = logging.getLogger(__name__)


def generate_token():
    return base64.b16encode(os.urandom(32)).lower()


def validate_image(image):
    brightness = rate_brightness(image)
    return brightness > 0.15


def rate_brightness(image):
    img = Image.open(io.BytesIO(image))
    return sum(ImageStat.Stat(img).mean[0:3]) / 3. / 255.


def send_registration_email(email, token, username, display_name):
    context = {
        'token': token,
        'username': username,
        'display_name': display_name
    }
    plain = render_to_string('credocommon/registration_email.txt', context)
    html = render_to_string('credocommon/registration_email.html', context)

    send_mail('Credo API registration', plain, 'CREDO <credoapi@credo.science>', [email], html_message=html)


def register_user(email, password, username, display_name, team):
    from credocommon.exceptions import RegistrationException
    from credocommon.models import User, Team

    user = None

    try:
        u = User.objects.get(email=email)
        if not u.is_active:
            user = u
            user.team = Team.objects.get_or_create(name=team)[0]
            user.display_name = display_name
            user.key = generate_token()
            user.username = username
            user.email_confirmation_token = generate_token()
            user.set_password(password)
            user.save()
            logger.info('Updating user info and resending activation email to user {}'.format(user))
    except User.DoesNotExist:
        logger.info('Creating new user {} {}'.format(username, display_name))

    if not user:
        try:
            user = User.objects.create_user(
                team=Team.objects.get_or_create(name=team)[0],
                display_name=display_name,
                key=generate_token(),
                password=password,
                username=username,
                email=email,
                is_active=False,
                email_confirmation_token=generate_token(),
            )
        except IntegrityError:
            logger.warning('User registration failed, IntegrityError')
            raise RegistrationException("User with given username or email already exists.")

    if user:
        logger.info('Sending registration email to {}'.format(user.email))
        try:
            send_registration_email(user.email, user.email_confirmation_token, user.username, user.display_name)
        except Exception as e:
            logger.exception(e)
            logger.error('Failed to send confirmation email for user {} ({})'.format(user, user.email))
