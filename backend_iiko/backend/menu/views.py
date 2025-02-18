from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from django.contrib.sites.shortcuts import get_current_site

from .models import Product, Category, Kitchen
from .serializers import (GetProductSerializer, GetKitchenSerializer,
                          GetCategorySerializer,)

@extend_schema_view(
    list=extend_schema(
        summary="Получить список продуктов",
        description="Возвращает список всех продуктов.",
        tags=['Product'],
    ),
    retrieve=extend_schema(
        summary="Получить детали продукта",
        description="Возвращает детали конкретного продукта по его ID.",
        tags=['Product'],
    ),
    create=extend_schema(
        summary="Создать новый продукт",
        description="Создает новый продукт.",
        tags=['Product'],
    ),
    update=extend_schema(
        summary="Обновить продукт",
        description="Полностью обновляет продукт по его ID.",
        tags=['Product'],
    ),
    partial_update=extend_schema(
        summary="Частично обновить продукт",
        description="Частично обновляет продукт по его ID.",
        tags=['Product'],
    ),
    destroy=extend_schema(
        summary="Удалить продукт",
        description="Удаляет продукт по его ID.",
        tags=['Product'],
    ),
)
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = GetProductSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Получить список категорий",
        description="Возвращает список всех категорий.",
        tags=['Category'],
    ),
    retrieve=extend_schema(
        summary="Получить детали категории",
        description="Возвращает детали конкретной категории по её ID.",
        tags=['Category'],
    ),
    create=extend_schema(
        summary="Создать новую категорию",
        description="Создает новую категорию.",
        tags=['Category'],
    ),
    update=extend_schema(
        summary="Обновить категорию",
        description="Полностью обновляет категорию по её ID.",
        tags=['Category'],
    ),
    partial_update=extend_schema(
        summary="Частично обновить категорию",
        description="Частично обновляет категорию по её ID.",
        tags=['Category'],
    ),
    destroy=extend_schema(
        summary="Удалить категорию",
        description="Удаляет категорию по её ID.",
        tags=['Category'],
    ),
)
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = GetCategorySerializer



@extend_schema_view(
    list=extend_schema(
        summary="Получить список кухонь",
        description="Возвращает список всех кухонь.",
        tags=['Kitchen'],
    ),
    retrieve=extend_schema(
        summary="Получить детали кухни",
        description="Возвращает детали конкретной кухни по её ID.",
        tags=['Kitchen'],
    ),
    create=extend_schema(
        summary="Создать новую кухню",
        description="Создает новую кухню.",
        tags=['Kitchen'],
    ),
    update=extend_schema(
        summary="Обновить кухню",
        description="Полностью обновляет кухню по её ID.",
        tags=['Kitchen'],
    ),
    partial_update=extend_schema(
        summary="Частично обновить кухню",
        description="Частично обновляет кухню по её ID.",
        tags=['Kitchen'],
    ),
    destroy=extend_schema(
        summary="Удалить кухню",
        description="Удаляет кухню по её ID.",
        tags=['Kitchen'],
    ),
)
class KitchenViewSet(ModelViewSet):
    queryset = Kitchen.objects.all()
    serializer_class = GetKitchenSerializer
