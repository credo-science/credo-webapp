from __future__ import unicode_literals

import base64
import io
import os

from PIL import Image, ImageStat


def generate_token():
    return base64.b16encode(os.urandom(32)).lower()


def filter_brightness(image):
    img = Image.open(io.BytesIO(base64.decodestring(image))).convert('L')  # Convert to greyscale
    return ImageStat.Stat(img).mean[0] < 100  # Mean brightness less than 100/255
