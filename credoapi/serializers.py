from rest_framework import serializers
from credoapi.models import Detection, Device, Team, User
from credoapi.helpers import Frame, Header, Body


# Body

class DeviceInfoSerializer(serializers.Serializer):
    androidVersion = serializers.CharField(max_length=10)
    deviceId = serializers.CharField(max_length=50)
    deviceModel = serializers.CharField(max_length=50)


class UserInfoSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    key = serializers.CharField(max_length=20, required=False)
    name = serializers.CharField(max_length=50)
    team = serializers.CharField(max_length=50)


class BodySerializer(serializers.Serializer):
    device_info = DeviceInfoSerializer(required=False)
    user_info = UserInfoSerializer(required=False)

    def create(self, validated_data):
        return Body(**validated_data)

    def update(self, instance, validated_data):
        instance.device_info = validated_data.get('device_info', instance.device_info)
        instance.user_info = validated_data.get('user_info', instance.user_info)


# Header

class HeaderSerializer(serializers.Serializer):
    application = serializers.CharField(max_length=10)
    frame_type = serializers.CharField(max_length=10)
    protocol = serializers.CharField(max_length=10)
    time_stamp = serializers.IntegerField()

    def create(self, validated_data):
        return Header(**validated_data)

    def update(self, instance, validated_data):
        instance.application = validated_data.get('application', instance.application)
        instance.frame_type = validated_data.get('frame_type', instance.frame_type)
        instance.protocol = validated_data.get('protocol', instance.protocol)
        instance.time_stamp = validated_data.get('time_stamp', instance.time_stamp)


# Frame

class FrameSerializer(serializers.Serializer):
    header = HeaderSerializer()
    body = BodySerializer()

    def create(self, validated_data):
        return Frame(**validated_data)

    def update(self, instance, validated_data):
        instance.header = validated_data.get('header', instance.header)
        instance.body = validated_data.get('body', instance.body)

    # validate if body has all required fields
    # check if key is provided
