from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from django_filters.rest_framework import DjangoFilterBackend

from organization.models import Restaurant

from .models import Product, Category, Kitchen
from .serializers import (GetCategorySerializer, PostPatchCategorySerializer,
                          AddRestaurantToCategorySerializer, GetKitchenSerializer,
                          PostPatchKitchenSerializer, AddRestaurantToKitchenSerializer)
from .filters import CategoryFilter, KitchenFilter


@extend_schema_view(
    list=extend_schema(
        summary='Get list of categories',
        parameters=[
            OpenApiParameter(name='name', type=str, location=OpenApiParameter.QUERY, description='Filter by restaurant name'),
            OpenApiParameter(name='restaurant', type=str, location=OpenApiParameter.QUERY, description='Filter by restaurant name')],
        tags=['Categories']),
    retrieve=extend_schema(
        summary='Get category by id',
        tags=['Categories']),
    create=extend_schema(
        summary='Create new category',
        tags=['Categories']),
    update=extend_schema(
        summary='Update category',
        tags=['Categories']),
    partial_update=extend_schema(
        summary='Partial update category',
        tags=['Categories']),
    destroy=extend_schema(
        summary='Delete category',
        tags=['Categories']),
    add_restaurant_to_category=extend_schema(
        summary='Add restaurant to category',
        tags=['Categories'],
        request=AddRestaurantToCategorySerializer),
    delete_restaurant_to_category=extend_schema(
        summary='Delete restaurant from category',
        tags=['Categories'],
        parameters=[
            OpenApiParameter(name='category_id', type=int, location=OpenApiParameter.QUERY, description='Category id'),
            OpenApiParameter(name='restaurant_id', type=int, location=OpenApiParameter.QUERY, description='Restaurant id')]
    )
)
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = GetCategorySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return PostPatchCategorySerializer
        return GetCategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(GetCategorySerializer(serializer.instance).data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(GetCategorySerializer(serializer.instance).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        for restaurant in instance.restaurant.all():
            if user not in restaurant.chain.organization.authors.all():
                return Response({'You are not an author of this restaurant'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def add_restaurant_to_category(self, request):
        serializer = AddRestaurantToCategorySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        return Response(GetCategorySerializer(category).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_restaurant_to_category(self, request):
        category_id = request.query_params.get('category_id')
        restaurant_id = request.query_params.get('restaurant_id')

        user = request.user
        category = Category.objects.filter(id=category_id).first()
        restaurant = Restaurant.objects.filter(id=restaurant_id).first()

        if category is None:
            return Response({'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        if restaurant is None:
            return Response({'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)

        if user not in restaurant.chain.organization.authors.all():
            return Response({'You are not an author of this restaurant'}, status=status.HTTP_403_FORBIDDEN)

        if restaurant not in category.restaurant.all():
            return Response({'Restaurant not in category'}, status=status.HTTP_404_NOT_FOUND)

        for restaurant_ in category.restaurant.all():
            if user not in restaurant_.chain.organization.authors.all():
                return Response({'You are not an author of this restaurant'}, status=status.HTTP_403_FORBIDDEN)

        category.restaurant.remove(restaurant)

        return Response(GetCategorySerializer(category).data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        summary='Get list of categories',
        parameters=[
            OpenApiParameter(name='name', type=str, location=OpenApiParameter.QUERY, description='Filter by restaurant name'),
            OpenApiParameter(name='restaurant', type=str, location=OpenApiParameter.QUERY, description='Filter by restaurant name')],
        tags=['Kitchen']),
    retrieve=extend_schema(
        summary='Get category by id',
        tags=['Kitchen']),
    create=extend_schema(
        summary='Create new category',
        tags=['Kitchen']),
    update=extend_schema(
        summary='Update category',
        tags=['Kitchen']),
    partial_update=extend_schema(
        summary='Partial update category',
        tags=['Kitchen']),
    destroy=extend_schema(
        summary='Delete category',
        tags=['Kitchen']),
    add_restaurant_to_kitchen=extend_schema(
        summary='Add restaurant to category',
        tags=['Kitchen'],
        request=AddRestaurantToKitchenSerializer),
    delete_restaurant_to_kitchen=extend_schema(
        summary='Delete restaurant from category',
        tags=['Kitchen'],
        parameters=[
            OpenApiParameter(name='kitchen_id', type=int, location=OpenApiParameter.QUERY, description='Category id'),
            OpenApiParameter(name='restaurant_id', type=int, location=OpenApiParameter.QUERY, description='Restaurant id')]
    )
)
class KitchenViewSet(ModelViewSet):
    queryset = Kitchen.objects.all()
    serializer_class = GetKitchenSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = KitchenFilter

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return PostPatchKitchenSerializer
        return GetKitchenSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(GetKitchenSerializer(serializer.instance).data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(GetKitchenSerializer(serializer.instance).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        for restaurant in instance.restaurant.all():
            if user not in restaurant.chain.organization.authors.all():
                return Response({'You are not an author of this restaurant'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def add_restaurant_to_kitchen(self, request):
        serializer = AddRestaurantToKitchenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        kitchen = serializer.save()
        return Response(GetKitchenSerializer(kitchen).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_restaurant_to_kitchen(self, request):
        kitchen_id = request.query_params.get('kitchen_id')
        restaurant_id = request.query_params.get('restaurant_id')

        user = request.user
        kitchen = Kitchen.objects.filter(id=kitchen_id).first()
        restaurant = Restaurant.objects.filter(id=restaurant_id).first()

        if kitchen is None:
            return Response({'Kitchen not found'}, status=status.HTTP_404_NOT_FOUND)

        if restaurant is None:
            return Response({'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)

        if user not in restaurant.chain.organization.authors.all():
            return Response({'You are not an author of this restaurant'}, status=status.HTTP_403_FORBIDDEN)

        if restaurant not in kitchen.restaurant.all():
            return Response({'Restaurant not in category'}, status=status.HTTP_404_NOT_FOUND)

        for restaurant_ in kitchen.restaurant.all():
            if user not in restaurant_.chain.organization.authors.all():
                return Response({'You are not an author of this restaurant'}, status=status.HTTP_403_FORBIDDEN)

        kitchen.restaurant.remove(restaurant)

        return Response(GetKitchenSerializer(kitchen).data, status=status.HTTP_200_OK)
