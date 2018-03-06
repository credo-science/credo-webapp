from rest_framework import serializers
from credoapi.models import Detection, Device, Team, User
from credoapi.helpers import InputHeader, Body, DetectionRequest


class DetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detection
        fields = (
            'id', 'accuracy', 'altitude', 'frame_content', 'height', 'width', 'd_id', 'latitude', 'longitude',
            'provider', 'timestamp'
        )


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = (
            'device_id', 'device_model', 'android_version', 'user'
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'team', 'email', 'name', 'key'
        )


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = (
            'name',
        )


class InputHeaderSerializer(serializers.Serializer):
    application = serializers.CharField(max_length=10)
    frame_type = serializers.CharField(max_length=10)
    protocol = serializers.CharField(max_length=10)
    time_stamp = serializers.IntegerField(min_value=0)

    def create(self, validated_data):
        print validated_data
        return InputHeader(**validated_data)


class BodySerializer(serializers.Serializer):
    detection = DetectionSerializer()
    device_info = DeviceSerializer()
    user_info = UserSerializer()

    def create(self, validated_data):
        detection_data = validated_data.pop('detection')
        device_info = validated_data.pop('device_info')
        user_info = validated_data.pop('user_info')
        detection = Detection(**detection_data)
        device = Device(**device_info)
        user = User(**user_info)
        return Body(detection, device, user)


class DetectionRequestSerializer(serializers.Serializer):
    header = InputHeaderSerializer(required=False)
    body = BodySerializer()

    def create(self, validated_data):
        header_data = validated_data.pop('header')
        body_data = validated_data.pop('body')
        body = Body(**body_data)
        header = InputHeader(**header_data)
        return DetectionRequest(header, body)
