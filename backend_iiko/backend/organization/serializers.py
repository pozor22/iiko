from rest_framework import serializers

from .models import Organization, Chain, Restaurant

from core.serializers import GetUserSerializer


class GetOrganizationSerializer(serializers.ModelSerializer):
    authors = GetUserSerializer(many=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'authors']
        read_only_fields = ['authors']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        organization = Organization.objects.create(**validated_data)
        if user and user.is_authenticated:
            organization.authors.add(user)
        return organization


class GetChainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chain
        fields = '__all__'


class GetRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
