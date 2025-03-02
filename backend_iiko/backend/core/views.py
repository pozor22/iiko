from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, PasswordChangeConfirmation
from .serializers import (GetUserSerializer, RegistrationUserRequestSerializer,
                          LoginSerializer, LoginWithCodeSerializer,
                          ChangeUsernameOrEmail, RefreshTokenSerializer,
                          ChangePasswordSerializer, ConfirmPasswordChangeSerializer,)
from .tasks import send_email_active_account, send_email_code
from .filters import UserFilter


@extend_schema_view(
    partial_update=extend_schema(exclude=True),
    list=extend_schema(
        summary="Получить список пользователей",
        description="Можно получить список всех пользователей, так же можно фильтровать по ролям, организациям, цепочкам и ресторанам",
        tags=['Users'],
        parameters=[
            OpenApiParameter(name='role', type=str, description='Filter for role, only many==true', required=False),
            OpenApiParameter(name='organizations', type=str, description='Filter for role, only many==true', required=False),
            OpenApiParameter(name='chains', type=str, description='Filter for role, only many==true', required=False),
            OpenApiParameter(name='restaurants', type=str, description='Filter for role, only many==true', required=False),]),
    retrieve=extend_schema(
        summary="Получить одного пользователя",
        description="Возвращает пользователя по его ID",
        tags=['Users'],),
    create=extend_schema(
        summary='Регистрация нового пользователя',
        description="Регистрация нового пользователя",
        tags=['Users'],
        request=RegistrationUserRequestSerializer,),
    destroy=extend_schema(
        summary="Удалить пользователя",
        description="Удаляет пользователя по её ID.",
        tags=['Users'],),
    login_user=extend_schema(
        summary='Авторизация пользователя',
        description="Авторизация пользователя по email и паролю",
        request=LoginSerializer,
        tags=['Auth']),
    login_user_with_code=extend_schema(
        summary='Авторизация пользователя по коду',
        description="Авторизация пользователя по коду",
        request=LoginWithCodeSerializer,
        tags=['Auth']),
    refresh_token=extend_schema(
        summary='Обновление access и refresh токенов',
        description='Обновление access и refresh токенов',
        request=RefreshTokenSerializer,
        tags=['Auth']),
    confirm_password_change=extend_schema(
        summary='Подтверждение смены пароля по коду',
        description='Подтверждение смены пароля по коду',
        tags=['Auth'],
        request=ConfirmPasswordChangeSerializer),
    resend_code=extend_schema(
        summary='Повторная отправка кода для смены пароля',
        description='Повторная отправка кода для смены пароля',
        tags=['Auth']),
    email_confirmed=extend_schema(
        summary='Подтверждение почты и активация пользователя',
        description='Подтверждение почты и активация пользователя',
        tags=['Auth']),
    change_username_or_email=extend_schema(
        summary='Смена имени или почты пользователя',
        description='Можно сменить только имя или только почту, так же можно сменить и имя и почту'
                'если менять почту, то на новую почту будет отправлено письмо для подтверждения',
        tags=['Users'],
        request=ChangeUsernameOrEmail),
    change_password=extend_schema(
        summary='Смена пароля пользователя',
        description='При смене пароля, на почту прийдет код для подтверждения',
        tags=['Users'],
        request=ChangePasswordSerializer),
)
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = GetUserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def create(self, request, *args, **kwargs):
        serializer = RegistrationUserRequestSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            current_site = get_current_site(request)
            domain = current_site.domain
            send_email_active_account.delay(user.id, domain)

            response = GetUserSerializer(user)

            return Response(response.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "PATCH не разрешен."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['post'])
    def login_user(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login_user_with_code(self, request):
        serializer = LoginWithCodeSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def refresh_token(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def confirm_password_change(self, request):
        serializer = ConfirmPasswordChangeSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = request.user
            new_password = request.session.get('new_password')

            if new_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                user.password_change_confirmation.delete()
                return Response({'message': 'Пароль успешно изменен'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def resend_code(self, request):
        user = request.user
        confirmation, _ = PasswordChangeConfirmation.objects.get_or_create(user=user)
        confirmation.generate_confirmation_code()
        send_email_code.delay(user.id, confirmation.code)

        return Response({'message': 'Код подтверждения отправлен на email'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def email_confirmed(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()

            serializer = GetUserSerializer(user)
            return Response({'message': 'Email confirmed', **serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Email confirmation failed'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['PATCH'], permission_classes=[IsAuthenticated])
    def change_username_or_email(self, request):
        user = request.user
        serializer = ChangeUsernameOrEmail(user, data=request.data, partial=True)
        if serializer.is_valid():
            if serializer.validated_data.get('username') and serializer.validated_data.get('email'):
                serializer.save()
                serializer = GetUserSerializer(user)

                current_site = get_current_site(request)
                domain = current_site.domain
                send_email_active_account.delay(user.id, domain)

                return Response({'message': 'Username and email changed', **serializer.data}, status=status.HTTP_200_OK)
            elif serializer.validated_data.get('username'):
                serializer.save()
                serializer = GetUserSerializer(user)

                return Response({'message': 'Username changed', **serializer.data}, status=status.HTTP_200_OK)
            else:
                serializer.save()
                serializer = GetUserSerializer(user)

                current_site = get_current_site(request)
                domain = current_site.domain
                send_email_active_account.delay(user.id, domain)

                return Response({'message': 'Email changed', **serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']

            confirmation, _ = PasswordChangeConfirmation.objects.get_or_create(user=user)
            confirmation.generate_confirmation_code()
            send_email_code.delay(user.id, confirmation.code)

            request.session['new_password'] = new_password

            return Response({'message': 'Код подтверждения отправлен на email'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
