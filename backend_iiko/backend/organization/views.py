from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from core.serializers import GetUserSerializer
from core.models import User

from backend.viewsets import MyModelViewSet

from .schemas import get_chain_schema, get_organization_schemas, get_restaurant_schemas
from .filters import ChainFilter, OrganizationFilter, RestaurantFilter
from .models import Organization, Chain, Restaurant
from .permissions import IsAuthorOrReadOnly, IsAuthorInChainOrReadOnly, IsAuthorInRestaurantOrReadOnly
from .serializers import (GetOrganizationSerializer, GetChainSerializer,
                          PostAddAuthorOrUserSerializer, PostPatchChainSerializer,
                          AddUserToChainSerializer, GetRestaurantSerializer,
                          PostPatchRestaurantSerializer, AddUserToRestaurantSerializer)


@get_organization_schemas
class OrganizationViewSet(MyModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = GetOrganizationSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrganizationFilter

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated, IsAuthorOrReadOnly])
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

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated, IsAuthorOrReadOnly])
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


@get_chain_schema
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

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
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


@get_restaurant_schemas
class RestaurantViewSet(ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = GetRestaurantSerializer
    permission_classes = [IsAuthenticated, IsAuthorInRestaurantOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RestaurantFilter

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return PostPatchRestaurantSerializer
        return GetRestaurantSerializer

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated, IsAuthorInRestaurantOrReadOnly])
    def add_user_in_restaurant(self, request) -> Response:
        serializer = AddUserToRestaurantSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)

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
