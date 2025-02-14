from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode

from .models import User
from .serializers import (GetUserSerializer, RegistrationUserRequestSerializer,
                          RegistrationUserResponsesSerializer, LoginSerializer,
                          UserConfirmSerializer)
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

# class UserConfirmEmailView(View):
#     def get(self, request, uidb64, token):
#         try:
#             uid = urlsafe_base64_decode(uidb64)
#             user = User.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#             user = None
#
#         if user is not None and default_token_generator.check_token(user, token):
#             user.is_active = True
#             user.save()
#             login(request, user)
#             return redirect('email_confirmed')
#         else:
#             return redirect('email_confirmation_failed')