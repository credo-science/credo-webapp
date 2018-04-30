from rest_framework import serializers

from credoapi.models import User, Team, Device


class RegisterRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=50)
    display_name = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=128)
    team = serializers.CharField(max_length=50)
    language = serializers.CharField(max_length=10)
    device_id = serializers.CharField(max_length=50)
    device_model = serializers.CharField(max_length=50)
    system_version = serializers.CharField(max_length=50)
    app_version = serializers.CharField(max_length=50)
