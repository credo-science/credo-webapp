from __future__ import unicode_literals

import base64
import io
import os

from PIL import Image, ImageStat


def generate_token():
    return base64.b16encode(os.urandom(32)).lower()


def validate_image(image):
    brightness = rate_brightness(image)
    return brightness > 0.15


def rate_brightness(image):
    img = Image.open(io.BytesIO(image))
    return sum(ImageStat.Stat(img).mean[0:3]) / 3. / 255.
