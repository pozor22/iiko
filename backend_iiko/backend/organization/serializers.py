from rest_framework import serializers

from .models import Organization, Chain, Restaurant

from core.serializers import GetUserSerializer
from core.models import User


class GetOrganizationSerializer(serializers.ModelSerializer):
    authors = GetUserSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'authors']
        read_only_fields = ['authors']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            organization = Organization.objects.create(**validated_data)
            organization.authors.add(user)
            user.organizations.add(organization)
            return organization

        raise serializers.ValidationError('User not found')


# Сериализотор для добавления автора в организацию или добавления пользователя в организацию
class PostAddAuthorOrUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    organization_id = serializers.IntegerField()

    def validate(self, value):
        user_id = value.get('user_id')
        organization_id = value.get('organization_id')
        author = self.context['request'].user

        user = User.objects.filter(id=user_id).first()
        organization = Organization.objects.filter(id=organization_id).first()

        if user is None:
            raise serializers.ValidationError('User not found')

        if user == author:
            raise serializers.ValidationError('You can not add yourself to organization')

        if organization is None:
            raise serializers.ValidationError('Organization not found')

        if author not in organization.authors.all():
            raise serializers.ValidationError('You are not an author of this organization')


        return value


    def create(self, validated_data):
        user = User.objects.get(id=validated_data.get('user_id'))
        organization = Organization.objects.get(id=validated_data.get('organization_id'))

        if self.context.get('add_author'):
            organization.authors.add(user)
            user.organizations.add(organization)

        else:
            user.organizations.add(organization)

        return {
            'user': GetUserSerializer(user).data,
            'organization': GetOrganizationSerializer(organization).data
        }


class GetChainSerializer(serializers.ModelSerializer):
    organization = GetOrganizationSerializer()

    class Meta:
        model = Chain
        fields = ['id', 'name', 'organization']


class PostPatchChainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chain
        fields = ['id', 'name', 'organization']


class GetRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
