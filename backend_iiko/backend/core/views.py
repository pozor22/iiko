from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode

from .models import User, PasswordChangeConfirmation
from .serializers import (GetUserSerializer, RegistrationUserRequestSerializer,
                          LoginSerializer, LoginWithCodeSerializer,
                          ChangeUsernameOrEmail, RefreshTokenSerializer,
                          ChangePasswordSerializer, ConfirmPasswordChangeSerializer,)
from .tasks import send_email_active_account, send_email_code


### Users
@extend_schema(
    request=RegistrationUserRequestSerializer,
    tags=['Users'])
@api_view(['POST'])
def create_user(request):
    serializer = RegistrationUserRequestSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        current_site = get_current_site(request)
        domain = current_site.domain
        send_email_active_account.delay(user.id, domain)

        response = GetUserSerializer(user)

        return Response(response.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Users'],
    parameters=[
        OpenApiParameter(name='many', type=bool,
                         description='Default False. If true, return all users with filter. /'
                                     'If false, return one user.', required=False),
        OpenApiParameter(name='pk', type=int, description='User id, only many==false', required=False),
        OpenApiParameter(name='role', type=str, description='Filter for role, only many==true', required=False),
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    many: bool = request.query_params.get('many', False)

    if many:
        pk: int = request.query_params.get('pk', None)
        if pk:
            return Response({'message': 'You cannot fill in the pk field together with many==True'},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            role: str = request.query_params.get('role', None)
            if role:
                users = User.objects.filter(groups__name=role)
            else:
                users = User.objects.all()
            serializer = GetUserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        pk: int = request.query_params.get('pk', None)
        if pk:
            user = User.objects.filter(pk=pk).first()
            if user:
                serializer = GetUserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
            serializer = GetUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['Users'],
                 parameters=[
                     OpenApiParameter(name='pk', type=int, description='User id', required=False),
                     OpenApiParameter(name='username', type=str, description='Username', required=False),
                     OpenApiParameter(name='email', type=str, description='Email', required=False),
                 ]
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser, IsAuthenticated])
def delete_user(request):
    pk = request.query_params.get('pk', None)
    username = request.query_params.get('username', None)
    email = request.query_params.get('email', None)

    if pk:
        user = User.objects.filter(pk=pk).first()
        user.delete()
        response = GetUserSerializer(user)
        return Response({'message': 'User deleted', **response.data}, status=status.HTTP_200_OK)
    elif username:
        user = User.objects.filter(username=username).first()
        user.delete()
        response = GetUserSerializer(user)
        return Response({'message': 'User deleted', **response.data}, status=status.HTTP_200_OK)
    elif email:
        user = User.objects.filter(email=email).first()
        user.delete()
        response = GetUserSerializer(user)
        return Response({'message': 'User deleted', **response.data}, status=status.HTTP_200_OK)

    return Response({'message': 'This endpoint needs to be deleted'}, status=status.HTTP_200_OK)


### Auth
@extend_schema(
    request=LoginSerializer,
    tags=['Auth'])
@api_view(['POST'])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=LoginWithCodeSerializer,
    tags=['Auth'])
@api_view(['POST'])
def login_user_with_code(request):
    serializer = LoginWithCodeSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=RefreshTokenSerializer,
    tags=['Auth']
)
@api_view(['POST'])
def refresh_token(request):
    serializer = RefreshTokenSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


### Change
@extend_schema(tags=['Change_user'], request=ChangeUsernameOrEmail)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def change_username(request):
    user = request.user
    serializer = ChangeUsernameOrEmail(user, data=request.data, partial=True)
    if serializer.is_valid():
        if serializer.validated_data.get('username') and serializer.validated_data.get('email'):
            serializer.save()
            user = request.user
            serializer = GetUserSerializer(user)
            current_site = get_current_site(request)
            domain = current_site.domain
            send_email_active_account.delay(user.id, domain)
            return Response({'message': 'Username and email changed', **serializer.data}, status=status.HTTP_200_OK)
        elif serializer.validated_data.get('username'):
            serializer.save()
            user = request.user
            serializer = GetUserSerializer(user)
            return Response({'message': 'Username changed', **serializer.data}, status=status.HTTP_200_OK)
        else:
            serializer.save()
            user = request.user
            serializer = GetUserSerializer(user)
            current_site = get_current_site(request)
            domain = current_site.domain
            send_email_active_account.delay(user.id, domain)
            return Response({'message': 'Email changed', **serializer.data}, status=status.HTTP_200_OK)


    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Change_user'], request=ChangePasswordSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        new_password = serializer.validated_data['new_password']

        # Генерируем код и отправляем email
        confirmation, _ = PasswordChangeConfirmation.objects.get_or_create(user=user)
        confirmation.generate_confirmation_code()
        send_email_code.delay(user.id, confirmation.code)

        # Сохраняем новый пароль в сессии
        request.session['new_password'] = new_password

        return Response({'message': 'Код подтверждения отправлен на email'}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


### Confirm
@extend_schema(tags=['Confirm'], request=ConfirmPasswordChangeSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_password_change(request):
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


@extend_schema(tags=['Confirm'])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_code(request):
    user = request.user
    confirmation, _ = PasswordChangeConfirmation.objects.get_or_create(user=user)
    confirmation.generate_confirmation_code()
    send_email_code.delay(user.id, confirmation.code)

    return Response({'message': 'Код подтверждения отправлен на email'}, status=status.HTTP_200_OK)


@extend_schema(tags=['Confirm'])
@api_view(['GET'])
def email_confirmed(request, uidb64, token):
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
