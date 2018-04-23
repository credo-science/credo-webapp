import base64
import os
from random import choice
import string
import time

CHARS = string.ascii_letters


class InputFrame(object):
    def __init__(self, header=None, body=None):
        self.header = header
        self.body = body


class OutputFrame(object):
    def __init__(self, header=None, body=None):
        self.header = header
        self.body = body


class InputHeader(object):
    def __init__(self, application=None, frame_type=None, protocol=None, time_stamp=None):
        self.application = application
        self.frame_type = frame_type
        self.protocol = protocol
        self.time_stamp = time_stamp


class OutputHeader(object):
    def __init__(self, server=None, frame_type=None, protocol=None, time_stamp=None):
        self.server = server
        self.frame_type = frame_type
        self.protocol = protocol
        self.time_stamp = int(time.time()) if time_stamp is None else time_stamp


class UserInfo(object):
    def __init__(self, team=None, email=None, name=None, key=None):
        self.team = team
        self.email = email
        self.name = name
        self.key = key


class KeyInfo(object):
    def __init__(self, key=None):
        self.key = key


class DeviceInfo(object):
    def __init__(self, deviceId=None, deviceModel=None, androidVersion=None):
        self.deviceId = deviceId
        self.deviceModel = deviceModel
        self.androidVersion = androidVersion


class DetectionInfo(object):
    def __init__(self,
                 id=None, accuracy=None, altitude=None, frame_content=None, height=None, width=None, latitude=None,
                 longitude=None, provider=None, timestamp=None
                 ):
        self.id = id
        self.accuracy = accuracy
        self.altitude = altitude
        self.frame_content = frame_content
        self.height = height
        self.width = width
        self.latitude = latitude
        self.longitude = longitude
        self.provider = provider
        self.timestamp = timestamp


class Body(object):
    def __init__(self, device_info=None, user_info=None, key_info=None, detection=None):
        self.device_info = DeviceInfo(**device_info) if device_info else None
        self.user_info = UserInfo(**user_info) if user_info else None
        self.key_info = KeyInfo(**key_info) if key_info else None
        self.detection_info = DetectionInfo(**detection) if detection else None


class OutputBody(object):
    def __init__(self, user_info=None):
        self.user_info = user_info


class Error(object):
    def __init__(self, error=None, message=None):
        self.error = error
        self.message = message


def generate_key():
    return ''.join(choice(CHARS) for _ in range(8))


def generate_token():
    return base64.b16encode(os.urandom(32)).lower()
