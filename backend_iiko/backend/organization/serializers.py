from django.views.decorators.http import require_GET
from rest_framework import serializers

from .models import Organization, Chain, Restaurant

from core.serializers import GetUserSerializer


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


class GetChainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chain
        fields = '__all__'


class GetRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
