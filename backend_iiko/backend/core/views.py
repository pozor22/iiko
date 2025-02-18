from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode

from .models import User
from .serializers import (GetUserSerializer, RegistrationUserRequestSerializer,
                          RegistrationUserResponsesSerializer, LoginSerializer,
                          LoginWithCodeSerializer, ChangeUsernameOrEmail)
from .tasks import send_email_active_account


@extend_schema(tags=['users'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_self_user(request):
    user = request.user
    serializer = GetUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=LoginSerializer,
    tags=['auth'])
@api_view(['POST'])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=LoginWithCodeSerializer,
    tags=['auth'])
@api_view(['POST'])
def login_user_with_code(request):
    serializer = LoginWithCodeSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=RegistrationUserRequestSerializer,
    tags=['auth'])
@api_view(['POST'])
def create_user(request):
    serializer = RegistrationUserRequestSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        current_site = get_current_site(request)
        domain = current_site.domain
        send_email_active_account.delay(user.id, domain)

        response = RegistrationUserResponsesSerializer(user)

        return Response(response.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['auth'])
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


### Change

@extend_schema(tags=['change'], request=ChangeUsernameOrEmail)
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
