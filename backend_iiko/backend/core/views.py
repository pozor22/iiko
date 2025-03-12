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

from .api_descriptions import user
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
        summary=user["get_user_list"]["summary"],
        description=user["get_user_list"]["description"],
        tags=['Users'],
        parameters=[
            OpenApiParameter(**param) for param in user["get_user_list"]["parameters"]
        ]
    ),
    retrieve=extend_schema(
        summary=user["get_user"]["summary"],
        description=user["get_user"]["description"],
        tags=['Users'],
    ),
    create=extend_schema(
        summary=user["create_user"]["summary"],
        description=user["create_user"]["description"],
        tags=['Users'],
        request=RegistrationUserRequestSerializer,
    ),
    destroy=extend_schema(
        summary=user["delete_user"]["summary"],
        description=user["delete_user"]["description"],
        tags=['Users'],
    ),
    login_user=extend_schema(
        summary=user["login_user"]["summary"],
        description=user["login_user"]["description"],
        request=LoginSerializer,
        tags=['Auth']
    ),
    login_user_with_code=extend_schema(
        summary=user["login_user_with_code"]["summary"],
        description=user["login_user_with_code"]["description"],
        request=LoginWithCodeSerializer,
        tags=['Auth']
    ),
    refresh_token=extend_schema(
        summary=user["refresh_token"]["summary"],
        description=user["refresh_token"]["description"],
        request=RefreshTokenSerializer,
        tags=['Auth']
    ),
    confirm_password_change=extend_schema(
        summary=user["confirm_password_change"]["summary"],
        description=user["confirm_password_change"]["description"],
        request=ConfirmPasswordChangeSerializer,
        tags=['Auth']
    ),
    resend_code=extend_schema(
        summary=user["resend_code"]["summary"],
        description=user["resend_code"]["description"],
        tags=['Auth']
    ),
    email_confirmed=extend_schema(
        summary=user["email_confirmed"]["summary"],
        description=user["email_confirmed"]["description"],
        parameters=[
            OpenApiParameter(name="uidb64", type=str, location=OpenApiParameter.QUERY,
                             description="Base64-encoded user ID"),
            OpenApiParameter(name="token", type=str, location=OpenApiParameter.QUERY,
                             description="Token for email confirmation"),
        ],
        request=None,
        tags=['Auth']
    ),
    change_username_or_email=extend_schema(
        summary=user["change_username_or_email"]["summary"],
        description=user["change_username_or_email"]["description"],
        request=ChangeUsernameOrEmail,
        tags=['Users']
    ),
    change_password=extend_schema(
        summary=user["change_password"]["summary"],
        description=user["change_password"]["description"],
        request=ChangePasswordSerializer,
        tags=['Users']
    )
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

            send_email_active_account.delay(user.id)

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
    def email_confirmed(self, request):
        uidb64 = request.query_params.get('uidb64')
        token = request.query_params.get('token')

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
