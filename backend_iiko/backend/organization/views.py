from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view

from core.serializers import GetUserSerializer
from core.models import User

from .models import Organization, Chain, Restaurant
from .permissions import IsAuthorOrReadOnly, IsAuthorInChainOrReadOnly
from .serializers import (GetOrganizationSerializer, GetChainSerializer,
                          GetRestaurantSerializer, PostAddAuthorOrUserSerializer,
                          PostPatchChainSerializer, AddUserToChainSerializer)


@extend_schema_view(
    list=extend_schema(
        summary="Получить список организаций",
        description="Возвращает список всех организаций. Но можно указывать только один параметр, два одновременно нельзя",
        tags=['Organization'],
        parameters=[
            OpenApiParameter(name='my_organization', type=bool,
                             description='Если True, возвращает только организации, где текущий пользователь является автором.'),
            OpenApiParameter(name='me_in_organization', type=bool,
                             description='Если True, возвращает только организации, где текущий пользователь находится в организациях.')
        ]),
    retrieve=extend_schema(
        summary="Получить детали организации",
        description="Возвращает детали конкретной организации по её ID.",
        tags=['Organization']),
    create=extend_schema(
        summary="Создать новую организацию",
        description="Создает новую организацию.",
        tags=['Organization']),
    partial_update=extend_schema(
        summary="Частично обновить организацию",
        description="Частично обновляет организацию по её ID.",
        tags=['Organization']),
    destroy=extend_schema(
        summary="Удалить организацию",
        description="Удаляет организацию по её ID.",
        tags=['Organization']),
    add_author=extend_schema(
        summary="Добавить автора в организацию",
        description="Позволяет текущим авторам добавлять новых авторов в организацию.",
        tags=['Organization'],
        request=PostAddAuthorOrUserSerializer),
    delete_author=extend_schema(
        summary="Удалить автора из организации",
        description="Позволяет удалить текущего пользователя из организации",
        tags=['Organization']),
    add_user_in_organization=extend_schema(
        summary="Добавить пользователя в организацию",
        description="Позволяет добавить пользователя в организацию по id пользователя и по id организации.",
        tags=['Organization'],
        request=PostAddAuthorOrUserSerializer),
    delete_user_in_organization=extend_schema(
        summary="Удалить пользователя из организации",
        description="Позволяет удалить пользователя из организации по id пользователя и по id организации.",
        tags=['Organization'],
        parameters=[
            OpenApiParameter(name='user_id', type=int, description='ID пользователя'),
            OpenApiParameter(name='organization_id', type=int, description='ID организации')
        ]),
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user = request.user
        user.organizations.add(serializer.instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
        summary="Получить список сетей",
        description="Возвращает список всех сетей. ",
        tags=['Chain'],
        parameters=[
            OpenApiParameter(name='my_chain', type=bool,
                             description='Если True, возвращает только сети, где текущий пользователь является автором.'),
            OpenApiParameter(name='me_in_chain', type=bool,
                             description='Если True, то возвращает сети в которых находится текущий пользователь.'),
        ]),
    retrieve=extend_schema(
        summary="Получить детали сети",
        description="Возвращает информацию о конкретной сети по её ID.",
        tags=['Chain'],),
    create=extend_schema(
        summary="Создать новую сеть",
        description="Создает новую сеть.",
        tags=['Chain'],
        request=PostPatchChainSerializer,),
    partial_update=extend_schema(
        summary="Частично обновить сеть",
        description="Можно обновить имя или организацию сети по отдельности.",
        tags=['Chain'],
        request=PostPatchChainSerializer,),
    destroy=extend_schema(
        summary="Удалить сеть",
        description="Удаляет сеть по её ID.",
        tags=['Chain'],),
    add_user_in_chain=extend_schema(
        summary="Добавить пользователя в сеть",
        description="Можно добавить пользователя в сеть по ID пользователя и ID сети.",
        tags=['Chain'],
        request=AddUserToChainSerializer,),
    delete_user_in_chain=extend_schema(
        summary="Удалить пользователя из сети",
        description="Удаляет пользователя из сети по ID пользователя и ID сети.",
        tags=['Chain'],
        parameters=[
            OpenApiParameter(name='user_id', type=int,
                             description='Нужно указать ID пользователя, которого нужно удалить из сети.'),
            OpenApiParameter(name='chain_id', type=int,
                             description='Нужно указать ID сети, из которой нужно удалить пользователя.'),
        ]),
)
class ChainViewSet(ModelViewSet):
    queryset = Chain.objects.all()
    serializer_class = GetChainSerializer
    permission_classes = [IsAuthenticated, IsAuthorInChainOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return PostPatchChainSerializer
        return GetChainSerializer

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    def list(self, request, *args, **kwargs):
        my_chain = request.query_params.get('my_chain', '').lower() == 'true'
        me_in_chain = request.query_params.get('me_in_chain', '').lower() == 'true'

        if my_chain:
            queryset = self.get_queryset().filter(organization__authors=request.user)
        elif me_in_chain:
            queryset = self.get_queryset().filter(organization__users=request.user)
        else:
            queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        organization_id = request.data.get('organization')

        if Organization.objects.filter(id=organization_id, authors=request.user).exists():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            user = request.user
            user.chains.add(serializer.instance)
            return Response(GetChainSerializer(serializer.instance).data, status=status.HTTP_201_CREATED, headers=headers)
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

        return Response(GetChainSerializer(serializer.instance).data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsAuthorInChainOrReadOnly])
    def add_user_in_chain(self, request) -> Response:
        serializer = AddUserToChainSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated, IsAuthorInChainOrReadOnly])
    def delete_user_in_chain(self, request):
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
