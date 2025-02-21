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
                          GetRestaurantSerializer, PostAddAuthorSerializer)

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
        request=PostAddAuthorSerializer,
    ),
)
class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = GetOrganizationSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    def list(self, request, *args, **kwargs):
        my_organization = request.query_params.get('my_organization', '').lower() == 'true'

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

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsAuthorOrReadOnly])
    def add_author(self, request):
        serializer = PostAddAuthorSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
