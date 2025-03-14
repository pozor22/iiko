from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view

from core.serializers import GetUserSerializer
from core.models import User

from backend.viewsets import MyModelViewSet

from .filters import ChainFilter
from .api_descriptions import restaurant, organization, chain_des
from .models import Organization, Chain, Restaurant
from .permissions import IsAuthorOrReadOnly, IsAuthorInChainOrReadOnly, IsAuthorInRestaurantOrReadOnly
from .serializers import (GetOrganizationSerializer, GetChainSerializer,
                          PostAddAuthorOrUserSerializer, PostPatchChainSerializer,
                          AddUserToChainSerializer, GetRestaurantSerializer,
                          PostPatchRestaurantSerializer, AddUserToRestaurantSerializer)


@extend_schema_view(
    list=extend_schema(
        summary=organization["get_list_organizations"]["summary"],
        description=organization["get_list_organizations"]["description"],
        tags=['Organization'],
        parameters=[
            OpenApiParameter(**param) for param in organization["get_list_organizations"]["parameters"]
        ]
    ),
    retrieve=extend_schema(
        summary=organization["get_organization"]["summary"],
        description=organization["get_organization"]["description"],
        tags=['Organization'],
    ),
    create=extend_schema(
        summary=organization["create_organization"]["summary"],
        description=organization["create_organization"]["description"],
        tags=['Organization'],
    ),
    partial_update=extend_schema(
        summary=organization["partial_update_organization"]["summary"],
        description=organization["partial_update_organization"]["description"],
        tags=['Organization'],
    ),
    destroy=extend_schema(
        summary=organization["delete_organization"]["summary"],
        description=organization["delete_organization"]["description"],
        tags=['Organization'],
    ),
    add_author=extend_schema(
        summary=organization["add_author"]["summary"],
        description=organization["add_author"]["description"],
        tags=['Organization'],
        request=PostAddAuthorOrUserSerializer,
    ),
    delete_author=extend_schema(
        summary=organization["delete_author"]["summary"],
        description=organization["delete_author"]["description"],
        tags=['Organization'],
    ),
    add_user_in_organization=extend_schema(
        summary=organization["add_user_in_organization"]["summary"],
        description=organization["add_user_in_organization"]["description"],
        tags=['Organization'],
        request=PostAddAuthorOrUserSerializer,
    ),
    delete_user_in_organization=extend_schema(
        summary=organization["delete_user_in_organization"]["summary"],
        description=organization["delete_user_in_organization"]["description"],
        tags=['Organization'],
        parameters=[
            OpenApiParameter(**param) for param in organization["delete_user_in_organization"]["parameters"]
        ],
    ),
)
class OrganizationViewSet(MyModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = GetOrganizationSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def list(self, request, *args, **kwargs):
        my_organization: bool = request.query_params.get('my_organization', '').lower() == 'true'
        me_in_organization: bool = request.query_params.get('me_in_organization', '').lower() == 'true'

        if my_organization:
            queryset = self.get_queryset().filter(authors=request.user)
        elif me_in_organization:
            queryset = self.get_queryset().filter(users=request.user)
        else:
            queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsAuthorOrReadOnly])
    def add_author(self, request):
        serializer = PostAddAuthorOrUserSerializer(data=request.data, context={'request': request, 'add_author': True})

        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsAuthorOrReadOnly])
    def delete_author(self, request, pk: int):
        organization = Organization.objects.filter(id=pk).first()
        user = request.user

        if not organization:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        if user not in organization.authors.all():
            return Response({'error': 'You are not an author of this organization'}, status=status.HTTP_403_FORBIDDEN)

        organization.authors.remove(user)
        user.organizations.remove(organization)
        return Response(GetOrganizationSerializer(organization).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsAuthorOrReadOnly])
    def add_user_in_organization(self, request):
        serializer = PostAddAuthorOrUserSerializer(data=request.data, context={'request': request, 'add_author': False})

        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated, IsAuthorOrReadOnly])
    def delete_user_in_organization(self, request):
        user_id: int = request.query_params.get('user_id')
        organization_id: int = request.query_params.get('organization_id')

        user = User.objects.get(id=user_id)
        organization = Organization.objects.get(id=organization_id)

        if request.user not in organization.authors.all():
            return Response({'error': 'You are not the author of this organization'}, status=status.HTTP_403_FORBIDDEN)

        if organization not in user.organizations.all():
            return Response({'error': 'User not found in this organization'}, status=status.HTTP_404_NOT_FOUND)

        user.organizations.remove(organization)

        return Response(GetUserSerializer(user).data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        summary=chain_des["get_list_chains"]["summary"],
        description=chain_des["get_list_chains"]["description"],
        tags=['Chain'],
    ),
    retrieve=extend_schema(
        summary=chain_des["get_chain"]["summary"],
        description=chain_des["get_chain"]["description"],
        tags=['Chain'],
    ),
    create=extend_schema(
        summary=chain_des["create_chain"]["summary"],
        description=chain_des["create_chain"]["description"],
        tags=['Chain'],
    ),
    partial_update=extend_schema(
        summary=chain_des["partial_update_chain"]["summary"],
        description=chain_des["partial_update_chain"]["description"],
        tags=['Chain'],
    ),
    destroy=extend_schema(
        summary=chain_des["delete_chain"]["summary"],
        description=chain_des["delete_chain"]["description"],
        tags=['Chain'],
    ),
    add_user_in_chain=extend_schema(
        summary=chain_des["add_user_in_chain"]["summary"],
        description=chain_des["add_user_in_chain"]["description"],
        tags=['Chain'],
        request=AddUserToChainSerializer,
    ),
    delete_user_in_chain=extend_schema(
        summary=chain_des["delete_user_in_chain"]["summary"],
        description=chain_des["delete_user_in_chain"]["description"],
        tags=['Chain'],
        parameters=[
            OpenApiParameter(**param) for param in chain_des["delete_user_in_chain"]["parameters"]
        ],
    ),
)
class ChainViewSet(MyModelViewSet):
    queryset = Chain.objects.all()
    serializer_class = GetChainSerializer
    permission_classes = [IsAuthenticated, IsAuthorInChainOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = ChainFilter

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return PostPatchChainSerializer
        return GetChainSerializer

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def add_user_in_chain(self, request) -> Response:
        serializer = AddUserToChainSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(GetUserSerializer(serializer.instance).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_user_in_chain(self, request) -> Response:
        user_id: int = request.query_params.get('user_id')
        chain_id: int = request.query_params.get('chain_id')

        user = User.objects.get(id=user_id)
        chain = Chain.objects.get(id=chain_id)

        if request.user not in chain.organization.authors.all():
            return Response({'error': 'You are not the author of this organization'}, status=status.HTTP_403_FORBIDDEN)

        if chain not in user.chains.all():
            return Response({'error': 'User not found in this chain'}, status=status.HTTP_404_NOT_FOUND)

        user.chains.remove(chain)

        return Response(GetUserSerializer(user).data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        summary=restaurant["get_list_restaurants"]["summary"],
        description=restaurant["get_list_restaurants"]["description"],
        tags=['Restaurant'],
        parameters=[
            OpenApiParameter(**param) for param in restaurant["get_list_restaurants"]["parameters"]
        ]
    ),
    retrieve=extend_schema(
        summary=restaurant["get_restaurant"]["summary"],
        description=restaurant["get_restaurant"]["description"],
        tags=['Restaurant'],
    ),
    create=extend_schema(
        summary=restaurant["create_restaurant"]["summary"],
        description=restaurant["create_restaurant"]["description"],
        tags=['Restaurant'],
        request=PostPatchRestaurantSerializer,
    ),
    partial_update=extend_schema(
        summary=restaurant["partial_update_restaurant"]["summary"],
        description=restaurant["partial_update_restaurant"]["description"],
        tags=['Restaurant'],
        request=PostPatchRestaurantSerializer,
    ),
    destroy=extend_schema(
        summary=restaurant["delete_restaurant"]["summary"],
        description=restaurant["delete_restaurant"]["description"],
        tags=['Restaurant'],
    ),
    add_user_in_restaurant=extend_schema(
        summary=restaurant["add_user_in_restaurant"]["summary"],
        description=restaurant["add_user_in_restaurant"]["description"],
        tags=['Restaurant'],
        request=AddUserToRestaurantSerializer,
    ),
    delete_user_in_restaurant=extend_schema(
        summary=restaurant["delete_user_in_restaurant"]["summary"],
        description=restaurant["delete_user_in_restaurant"]["description"],
        tags=['Restaurant'],
        parameters=[
            OpenApiParameter(**param) for param in restaurant["delete_user_in_restaurant"]["parameters"]
        ],
    ),
)
class RestaurantViewSet(ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = GetRestaurantSerializer
    permission_classes = [IsAuthenticated, IsAuthorInRestaurantOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return PostPatchRestaurantSerializer
        return GetRestaurantSerializer

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    def list(self, request, *args, **kwargs):
        my_restaurant = request.query_params.get('my_restaurant', '').lower() == 'true'
        me_in_restaurant = request.query_params.get('me_in_restaurant', '').lower() == 'true'

        if my_restaurant:
            queryset = self.get_queryset().filter(chain__organization__authors=request.user)
        elif me_in_restaurant:
            queryset = self.get_queryset().filter(chain__organization__users=request.user)
        else:
            queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        chain_id = request.data.get('chain')

        chain = Chain.objects.get(id=chain_id)

        if Organization.objects.filter(id=chain.organization.id, authors=request.user).exists():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            user = request.user
            user.restaurants.add(serializer.instance)
            return Response(GetRestaurantSerializer(serializer.instance).data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({'error': 'You are not an author of this organization'}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(GetRestaurantSerializer(serializer.instance).data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsAuthorInRestaurantOrReadOnly])
    def add_user_in_restaurant(self, request) -> Response:
        serializer = AddUserToRestaurantSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated, IsAuthorInRestaurantOrReadOnly])
    def delete_user_in_restaurant(self, request):
        user_id: int = request.query_params.get('user_id')
        restaurant_id: int = request.query_params.get('restaurant_id')

        user = User.objects.get(id=user_id)
        restaurant = Restaurant.objects.get(id=restaurant_id)

        if request.user not in restaurant.chain.organization.authors.all():
            return Response({'error': 'You are not the author of this organization'}, status=status.HTTP_403_FORBIDDEN)

        if restaurant not in user.restaurants.all():
            return Response({'error': 'User not found in this chain'}, status=status.HTTP_404_NOT_FOUND)

        user.restaurants.remove(restaurant)

        return Response(GetUserSerializer(user).data, status=status.HTTP_200_OK)
