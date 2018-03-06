from rest_framework import serializers
from credoapi.models import Detection, Device, Team, User


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
