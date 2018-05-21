from __future__ import unicode_literals

import base64
import io
import os

from PIL import Image, ImageStat

from django.core.mail import send_mail
from django.template.loader import render_to_string


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
    html = render_to_string('credocommon/registration_email.txt', context)

    send_mail('Credo API registration', plain, 'CREDO <credoapi@credo.science>', [email], html_message=html)
