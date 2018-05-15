from __future__ import unicode_literals

import base64
import io
import os

from PIL import Image, ImageStat


def generate_token():
    return base64.b16encode(os.urandom(32)).lower()


def validate_image(image):
    return rate_brightness(image) > 0.5


def rate_brightness(image):
    img = Image.open(io.BytesIO(image))
    return sum(ImageStat.Stat(img).mean[0:3]) / 3. / 255.
