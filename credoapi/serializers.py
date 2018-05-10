from rest_framework import serializers
from credoapi.helpers import InputFrame, InputHeader, Body

INPUT_FRAME_TYPES = ['detection', 'login', 'ping', 'register']
OUTPUT_FRAME_TYPES = ['login']


# WARNING: serializers for v1 api don't operate on model directly, no data is stored in db


class DeviceInfoSerializer(serializers.Serializer):
    deviceId = serializers.CharField(max_length=50)
    deviceModel = serializers.CharField(max_length=50)
    androidVersion = serializers.CharField(max_length=10)


class UserInfoSerializer(serializers.Serializer):
    team = serializers.CharField(max_length=50)
    email = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=50)
    key = serializers.CharField(max_length=20, required=False)


class KeyInfoSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=50)


class DetectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    accuracy = serializers.FloatField()
    altitude = serializers.FloatField()
    frame_content = serializers.CharField(max_length=5000, required=False)
    height = serializers.FloatField()
    width = serializers.IntegerField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    provider = serializers.CharField(max_length=20)
    timestamp = serializers.IntegerField()


# Body

class BodySerializer(serializers.Serializer):
    device_info = DeviceInfoSerializer(required=False)
    user_info = UserInfoSerializer(required=False)
    key_info = KeyInfoSerializer(required=False)
    detection = DetectionSerializer(required=False)


# Output Body

class OutputBodySerializer(serializers.Serializer):
    user_info = UserInfoSerializer(required=False)


# Header

class InputHeaderSerializer(serializers.Serializer):
    application = serializers.CharField(max_length=10)
    frame_type = serializers.CharField(max_length=10)
    protocol = serializers.CharField(max_length=10)
    time_stamp = serializers.IntegerField()

    def validate_frame_type(self, frame_type_raw):
        if frame_type_raw not in INPUT_FRAME_TYPES:
            raise serializers.ValidationError("Frame type must be one of types: %s" % ', '.join(INPUT_FRAME_TYPES))
        return frame_type_raw


# OutputHeader

class OutputHeaderSerializer(serializers.Serializer):
    server = serializers.CharField(max_length=10)
    frame_type = serializers.CharField(max_length=10)
    protocol = serializers.CharField(max_length=10)
    time_stamp = serializers.IntegerField()

    def validate_frame_type(self, frame_type_raw):
        if frame_type_raw not in OUTPUT_FRAME_TYPES:
            raise serializers.ValidationError("Frame type must be one of types: %s" % ', '.join(OUTPUT_FRAME_TYPES))
        return frame_type_raw


# InputFrame

def check_for_fields(validated, required_fields):
    if not set(required_fields).issubset(set(required_fields)):
        raise serializers.ValidationError("This frame is missing fields: %s" % ", ".join(required_fields))


class InputFrameSerializer(serializers.Serializer):
    header = InputHeaderSerializer()
    body = BodySerializer()

    def validate(self, data):
        frame_type = data['header']['frame_type']
        body_keys = data['body'].keys()

        if frame_type == 'detection':
            check_for_fields(body_keys, ('device_info', 'user_info', 'detection'))
            check_for_fields(data['body']['user_info'], ('key'))
        elif frame_type == 'login':
            check_for_fields(body_keys, ('device_info', 'key_info'))
        elif frame_type == 'ping':
            check_for_fields(body_keys, ('device_info', 'user_info'))
            check_for_fields(data['body']['user_info'], ('key'))
        elif frame_type == 'register':
            check_for_fields(body_keys, ('device_info', 'user_info'))
        else:
            raise serializers.ValidationError("Frame type must be one of types: %s" % ', '.join(INPUT_FRAME_TYPES))

        return data

    def create(self, validated_data):
        header = InputHeader(**validated_data.get('header'))
        body = Body(**validated_data.get('body'))

        return InputFrame(header=header, body=body)

    def update(self, instance, validated_data):
        instance.header = InputHeader(validated_data.get('header', instance.header))
        instance.body = Body(validated_data.get('body', instance.body))


# OutputFrame

class OutputFrameSerializer(serializers.Serializer):
    header = OutputHeaderSerializer()
    body = OutputBodySerializer()

    def validate(self, data):
        frame_type = data['header']['frame_type']
        body_keys = data['body'].keys()

        if frame_type == 'login':
            check_for_fields(body_keys, ('user_info'))
        else:
            raise serializers.ValidationError("Frame type must be one of types: %s" % ', '.join(OUTPUT_FRAME_TYPES))

        return data


class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField(max_length=20)
    message = serializers.CharField(max_length=255)
