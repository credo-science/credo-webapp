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
    team = serializers.CharField(max_length=50)
    language = serializers.CharField(max_length=10)


class LoginRequestSerializer(GenericRequestSerializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(max_length=50, required=False)
    password = serializers.CharField(max_length=128)


class InfoRequestSerializer(GenericRequestSerializer):
    display_name = serializers.CharField(max_length=50, required=False)
    team = serializers.CharField(max_length=50, required=False)
    language = serializers.CharField(max_length=10, required=False)
