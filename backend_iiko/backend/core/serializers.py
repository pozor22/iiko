from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.validators import MinValueValidator, MaxValueValidator

from .models import User


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'code', 'is_active']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError('Invalid username or password')

        if not user.is_active:
            raise serializers.ValidationError('User is not active')

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            }
        }


class LoginWithCodeSerializer(serializers.Serializer):
    code = serializers.IntegerField(validators=[MinValueValidator(100000), MaxValueValidator(999999)])

    def validate(self, attrs):
        code = attrs.get('code')

        user = authenticate(code=code)

        if not user:
            raise serializers.ValidationError('Invalid code')

        if not user.is_active:
            raise serializers.ValidationError('User is not active')

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            }
        }


class RegistrationUserRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        user.set_password(validated_data['password'])
        user.save()
        return user


class RegistrationUserResponsesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_active']


### Change
class ChangeUsernameOrEmail(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False}
        }

    def update(self, instance, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')

        if username:
            instance.username = username
        if email:
            instance.email = email
            instance.is_active = False
        instance.save()
        return instance
