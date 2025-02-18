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
            "user": GetUserSerializer(user).data
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
            "user": GetUserSerializer(user).data
        }


class RefreshTokenSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get('token')
        try:
            refresh = RefreshToken(token)
            user = User.objects.get(id=refresh['user_id'])
            return {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": GetUserSerializer(user).data
            }
        except Exception as e:
            raise serializers.ValidationError('Invalid token')


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


### Change
class ChangeUsernameOrEmail(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False}
        }

    def validate_username(self, value):
        if value == "":
            return None
        return value

    def validate_email(self, value):
        if value == "":
            return None
        return value

    def update(self, instance, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')

        if username is not None:
            instance.username = username
        if email is not None:
            instance.email = email
            instance.is_active = False
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')

        if new_password != confirm_new_password:
            raise serializers.ValidationError('Passwords do not match')

        user = authenticate(username=self.context['request'].user.username, password=old_password)

        if not user:
            raise serializers.ValidationError('Invalid password')

        return attrs


class ConfirmPasswordChangeSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate_code(self, value):
        user = self.context['request'].user
        confirmation = getattr(user, "password_change_confirmation", None)

        if not confirmation:
            raise serializers.ValidationError('Код не найден')

        if confirmation.code != value:
            raise serializers.ValidationError('Неверный код')

        if not confirmation.is_code_valid():
            raise serializers.ValidationError('Код устарел')

        return value
