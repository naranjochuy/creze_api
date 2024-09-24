from rest_framework import serializers
from .models import User
from utils.custom_serializers import CustomCharField


class PasswordSerializer(serializers.Serializer):

    password = serializers.CharField(max_length=100)


class LoginSerializer(PasswordSerializer):

    email = serializers.EmailField(max_length=80)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class MFAValidateSerializer(serializers.Serializer):

    code = CustomCharField(validate_regex={
        'regex': r'^\d{6}$', 'error_message': 'Código incompatible'
    })


class MFADisableSerializer(serializers.Serializer):

    code = CustomCharField(validate_regex={
        'regex': r'^.{10}$', 'error_message': 'Código incompatible'
    })


class MFAActivateSerializer(PasswordSerializer):

    pass
