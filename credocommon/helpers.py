# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import io
import os

from PIL import Image, ImageStat

from django.core.mail import send_mail
from django.db import IntegrityError
from django.template.loader import render_to_string

from credocommon.exceptions import RegistrationException
from credocommon.models import User, Team

import logging

logger = logging.getLogger(__name__)


def generate_token():
    return base64.b16encode(os.urandom(32)).lower().decode()


def validate_image(image):
    try:
        img = Image.open(io.BytesIO(image))
    except IOError:
        return False

    if get_average_brightness(img) > 0.15:
        return False

    # if get_max_brightness(img) < 120:
    #    return False

    return True


def get_average_brightness(img):
    return sum(ImageStat.Stat(img).mean[0:3]) / 3.0 / 255.0


def get_max_brightness(img):
    minima, maxima = img.convert("L").getextrema()
    return maxima


def send_registration_email(email, token, username, display_name):
    context = {"token": token, "username": username, "display_name": display_name}
    plain = render_to_string("credocommon/registration_email.txt", context)
    html = render_to_string("credocommon/registration_email.html", context)

    send_mail(
        "Credo API registration",
        plain,
        "CREDO <credoapi@credo.science>",
        [email],
        html_message=html,
    )


def register_user(email, password, username, display_name, team):
    user = None

    try:
        u = User.objects.get(email=email)
        if not u.is_active:
            try:
                user = u
                user.team = Team.objects.get_or_create(name=team)[0]
                user.display_name = display_name
                user.key = generate_token()
                user.username = username
                user.email_confirmation_token = generate_token()
                user.set_password(password)
                user.save()
            except IntegrityError:
                logger.warning("User registration failed, IntegrityError")
                raise RegistrationException(
                    "User with given username or email already exists."
                )
            logger.info(
                "Updating user info and resending activation email to user {}".format(
                    user
                )
            )
    except User.DoesNotExist:
        logger.info("Creating new user {} {}".format(username, display_name))

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
            logger.warning("User registration failed, IntegrityError")
            raise RegistrationException(
                "User with given username or email already exists."
            )

    if user:
        logger.info("Sending registration email to {}".format(user.email))
        try:
            send_registration_email(
                user.email,
                user.email_confirmation_token,
                user.username,
                user.display_name,
            )
        except Exception as e:
            logger.exception(e)
            logger.error(
                "Failed to send confirmation email for user {} ({})".format(
                    user, user.email
                )
            )
            raise e


def register_oauth_user(email, username, display_name, provider):
    logger.info(
        "Registering OAuth user: email={}, username={}, display_name={}, provider={}".format(
            email, username, display_name, provider
        )
    )
    try:
        user = User.objects.create_user(
            team=Team.objects.get_or_create(name="")[0],
            display_name=display_name,
            key=generate_token(),
            password=generate_token(),
            username=username,
            email=email,
            is_active=True,
        )
    except IntegrityError:
        logger.info("Username taken, creating random one")
        user = User.objects.create_user(
            team=Team.objects.get_or_create(name="")[0],
            display_name=display_name,
            key=generate_token(),
            password=generate_token(),
            username=provider + "_" + generate_token()[:8],
            email=email,
            is_active=True,
        )

    return user
