from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from .serializers import (AddUserToChainSerializer, PostAddAuthorOrUserSerializer,
                          PostPatchRestaurantSerializer, AddUserToRestaurantSerializer)


from .api_descriptions import chain_des, organization, restaurant


get_organization_schemas=extend_schema_view(
    list=extend_schema(
        summary=organization["get_list_organizations"]["summary"],
        description=organization["get_list_organizations"]["description"],
        tags=['Organization'],
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


get_chain_schema = extend_schema_view(
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


get_restaurant_schemas = extend_schema_view(
    list=extend_schema(
        summary=restaurant["get_list_restaurants"]["summary"],
        description=restaurant["get_list_restaurants"]["description"],
        tags=['Restaurant'],
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
    ),
    partial_update=extend_schema(
        summary=restaurant["partial_update_restaurant"]["summary"],
        description=restaurant["partial_update_restaurant"]["description"],
        tags=['Restaurant'],
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
