import base64
import os


def generate_token():
    return base64.b16encode(os.urandom(32)).lower()
