# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers


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


class OAuthLoginRequestSerializer(GenericRequestSerializer):
    authorization_code = serializers.CharField(max_length=128)
    provider = serializers.ChoiceField(choices=("scistarter",))


class InfoRequestSerializer(GenericRequestSerializer):
    display_name = serializers.CharField(max_length=50, required=False)
    team = serializers.CharField(max_length=50, allow_blank=True, required=False)
    language = serializers.CharField(max_length=10, required=False)


class DetectionSerializer(serializers.Serializer):
    accuracy = serializers.FloatField()
    altitude = serializers.FloatField()
    frame_content = serializers.CharField(
        max_length=40000, default="", allow_blank=True
    )
    height = serializers.IntegerField(required=False, default=None)
    width = serializers.IntegerField(required=False, default=None)
    x = serializers.IntegerField(required=False, default=None)
    y = serializers.IntegerField(required=False, default=None)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    provider = serializers.CharField(max_length=20)
    timestamp = serializers.IntegerField()
    metadata = serializers.CharField(max_length=10000, default="", allow_blank=True)


class DetectionRequestSerializer(GenericRequestSerializer):
    detections = DetectionSerializer(many=True)


class PingRequestSerializer(GenericRequestSerializer):
    timestamp = serializers.IntegerField()
    delta_time = serializers.IntegerField()
    on_time = serializers.IntegerField()
    metadata = serializers.CharField(max_length=10000, default="", allow_blank=True)


class DataExportRequestSerializer(serializers.Serializer):
    since = serializers.IntegerField()
    until = serializers.IntegerField()
    limit = serializers.IntegerField(max_value=500000)
    data_type = serializers.ChoiceField(choices=("detection", "ping"))


class MappingExportRequestSerializer(serializers.Serializer):
    mapping_type = serializers.ChoiceField(choices=("device", "user", "team"))
