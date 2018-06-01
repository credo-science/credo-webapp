from __future__ import unicode_literals

from rest_framework import serializers

from credocommon.models import Detection, Ping


class GenericRequestSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=50)
    device_type = serializers.CharField(max_length=50)
    device_model = serializers.CharField(max_length=50)
    system_version = serializers.CharField(max_length=50)
    app_version = serializers.CharField(max_length=50)


class RegisterRequestSerializer(GenericRequestSerializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=50)
    display_name = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=128)
    team = serializers.CharField(max_length=50, allow_blank=True)
    language = serializers.CharField(max_length=10)


class LoginRequestSerializer(GenericRequestSerializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(max_length=50, required=False)
    password = serializers.CharField(max_length=128)


class InfoRequestSerializer(GenericRequestSerializer):
    display_name = serializers.CharField(max_length=50, required=False)
    team = serializers.CharField(max_length=50, allow_blank=True, required=False)
    language = serializers.CharField(max_length=10, required=False)


class DetectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    accuracy = serializers.FloatField()
    altitude = serializers.FloatField()
    frame_content = serializers.CharField(max_length=5000, default="", allow_blank=True)
    height = serializers.IntegerField()
    width = serializers.IntegerField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    provider = serializers.CharField(max_length=20)
    timestamp = serializers.IntegerField()


class DetectionRequestSerializer(GenericRequestSerializer):
    detections = DetectionSerializer(many=True)


class PingRequestSerializer(GenericRequestSerializer):
    timestamp = serializers.IntegerField()
    delta_time = serializers.IntegerField()


class DataExportRequestSerializer(serializers.Serializer):
    since = serializers.IntegerField()
    until = serializers.IntegerField()
    limit = serializers.IntegerField(max_value=500000)
    data_type = serializers.ChoiceField(choices=('detection', 'ping'))
