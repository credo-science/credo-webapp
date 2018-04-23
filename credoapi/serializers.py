from rest_framework import serializers
from credoapi.models import Device, User, Detection, Team
from credoapi.helpers import InputFrame, InputHeader, OutputHeader, Body, KeyInfo, Error

INPUT_FRAME_TYPES = ['detection', 'login', 'ping', 'register']
OUTPUT_FRAME_TYPES = ['login']


class DeviceInfoSerializer(serializers.Serializer):
    deviceId = serializers.CharField(max_length=50)
    deviceModel = serializers.CharField(max_length=50)
    androidVersion = serializers.CharField(max_length=10)

    def create(self, validated_data):
        return Device(
            device_id=validated_data.get('deviceId'),
            device_model=validated_data.get('deviceModel'),
            android_version=validated_data.get('androidVersion')
        )

    def update(self, instance, validated_data):
        instance.device_id = validated_data.get('deviceId', instance.device_id)
        instance.device_model = validated_data.get('deviceModel', instance.device_model)
        instance.android_version = validated_data.get('androidVersion', instance.android_version)


class UserInfoSerializer(serializers.Serializer):
    team = serializers.CharField(max_length=50)
    email = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=50)
    key = serializers.CharField(max_length=20, required=False)

    def create(self, validated_data):
        # TODO: handle team
        return User(
            email=validated_data.get('email'),
            name=validated_data.get('name'),
            key=validated_data.get('key')
        )

    def update(self, instance, validated_data):
        instance.team = validated_data.get('team', instance.team)
        instance.email = validated_data.get('email', instance.email)
        instance.name = validated_data.get('name', instance.name)
        instance.key = validated_data.get('key', instance.key)


class KeyInfoSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=50)

    def create(self, validated_data):
        return KeyInfo(
            key=validated_data.get('key')
        )

    def update(self, instance, validated_data):
        instance.key = validated_data.get('key', instance.key)


class DetectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    accuracy = serializers.FloatField()
    altitude = serializers.FloatField()
    frame_content = serializers.CharField(max_length=5000)
    height = serializers.FloatField()
    width = serializers.IntegerField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    provider = serializers.CharField(max_length=20)
    timestamp = serializers.IntegerField()

    def create(self, validated_data):
        return Detection(
            d_id=validated_data.get('id'),
            accuracy=validated_data.get('accuracy'),
            altitude=validated_data.get('altitude'),
            frame_content=validated_data.get('frame_content'),
            height=validated_data.get('height'),
            width=validated_data.get('width'),
            latitude=validated_data.get('latitude'),
            longitude=validated_data.get('longitude'),
            provider=validated_data.get('provider'),
            timestamp=validated_data.get('timestamp')
        )

    def update(self, instance, validated_data):
        instance.d_id = validated_data.get('id', instance.d_id)
        instance.accuracy = validated_data.get('accuracy', instance.accuracy)
        instance.altitude = validated_data.get('altitude', instance.altitude)
        instance.frame_content = validated_data.get('frame_content', instance.frame_content)
        instance.height = validated_data.get('height', instance.height)
        instance.width = validated_data.get('width', instance.width)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.provider = validated_data.get('provider', instance.provider)
        instance.timestamp = validated_data.get('timestamp', instance.timestamp)


# Body

class BodySerializer(serializers.Serializer):
    device_info = DeviceInfoSerializer(required=False)
    user_info = UserInfoSerializer(required=False)
    key_info = KeyInfoSerializer(required=False)
    detection = DetectionSerializer(required=False)

    def create(self, validated_data):
        return Body(**validated_data)

    def update(self, instance, validated_data):
        instance.device_info = validated_data.get('device_info', instance.device_info)
        instance.user_info = validated_data.get('user_info', instance.user_info)
        instance.key_info = validated_data.get('key_info', instance.key_info)
        instance.detection = validated_data.get('detection', instance.detection)


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

    def create(self, validated_data):
        return InputHeader(**validated_data)

    def update(self, instance, validated_data):
        instance.application = validated_data.get('application', instance.application)
        instance.frame_type = validated_data.get('frame_type', instance.frame_type)
        instance.protocol = validated_data.get('protocol', instance.protocol)
        instance.time_stamp = validated_data.get('time_stamp', instance.time_stamp)


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

    def create(self, validated_data):
        return OutputHeader(**validated_data)

    def update(self, instance, validated_data):
        instance.server = validated_data.get('server', instance.application)
        instance.frame_type = validated_data.get('frame_type', instance.frame_type)
        instance.protocol = validated_data.get('protocol', instance.protocol)
        instance.time_stamp = validated_data.get('time_stamp', instance.time_stamp)


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
        header = InputHeader(validated_data.get('header'))
        body = Body(validated_data.get('body'))
        return InputFrame(header=header, body=body)

    def update(self, instance, validated_data):
        instance.header = InputHeader(validated_data.get('header', instance.header))
        instance.body = Body(validated_data.get('body', instance.body))


# OutputFrame

class OutputFrameSerializer(serializers.Serializer):
    header = OutputHeaderSerializer()
    body = BodySerializer()

    def validate(self, data):
        frame_type = data['header']['frame_type']
        body_keys = data['body'].keys()

        if frame_type == 'login':
            check_for_fields(body_keys, ('user_info'))
        else:
            raise serializers.ValidationError("Frame type must be one of types: %s" % ', '.join(OUTPUT_FRAME_TYPES))

        return data

    def create(self, validated_data):
        return InputFrame(**validated_data)

    def update(self, instance, validated_data):
        instance.header = validated_data.get('header', instance.header)
        instance.body = validated_data.get('body', instance.body)


class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField(max_length=20)
    message = serializers.CharField(max_length=255)

    def create(self, validated_data):
        return Error(**validated_data)

    def update(self, instance, validated_data):
        instance.error = validated_data.get('error', instance.application)
        instance.message = validated_data.get('message', instance.frame_type)
