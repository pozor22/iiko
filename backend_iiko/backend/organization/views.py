from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from django.contrib.sites.shortcuts import get_current_site

from .models import Organization, Chain, Restaurant
from .permissions import IsAuthorOrReadOnly
from .serializers import (GetOrganizationSerializer, GetChainSerializer,
                          GetRestaurantSerializer,)

from core.models import User


@extend_schema_view(
    list=extend_schema(
        summary="Получить список организаций",
        description="Возвращает список всех организаций.",
        tags=['Organization'],
        parameters=[
            OpenApiParameter(name='my_organization', type=bool,
                             description='Если True, возвращает только организации, где текущий пользователь является автором.')
        ]
    ),
    retrieve=extend_schema(
        summary="Получить детали организации",
        description="Возвращает детали конкретной организации по её ID.",
        tags=['Organization'],
    ),
    create=extend_schema(
        summary="Создать новую организацию",
        description="Создает новую организацию.",
        tags=['Organization'],
    ),
    update=extend_schema(
        summary="Обновить организацию",
        description="Полностью обновляет организацию по её ID.",
        tags=['Organization'],
    ),
    partial_update=extend_schema(
        summary="Частично обновить организацию",
        description="Частично обновляет организацию по её ID.",
        tags=['Organization'],
    ),
    destroy=extend_schema(
        summary="Удалить организацию",
        description="Удаляет организацию по её ID.",
        tags=['Organization'],
    ),
    add_author=extend_schema(
        summary="Добавить автора в организацию",
        description="Позволяет текущим авторам добавлять новых авторов в организацию.",
        tags=['Organization'],
    ),
)
class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = GetOrganizationSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def list(self, request, *args, **kwargs):
        my_organization = request.query_params.get('my_organization', False)

        if my_organization:
            queryset = self.get_queryset().filter(authors=request.user)
        else:
            queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAuthorOrReadOnly])
    def add_author(self, request, pk=None):
        organization = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({'user_id': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'user_id': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        organization.author.add(user)
        return Response({'message': f'User {user.username} added as an author.'}, status=status.HTTP_200_OK)
