from rest_framework import serializers

from .models import Category, Kitchen

from organization.serializers import GetRestaurantSerializer
from organization.models import Restaurant


class GetCategorySerializer(serializers.ModelSerializer):
    restaurant = GetRestaurantSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'restaurant']
        read_only_fields = ['restaurant']


class PostPatchCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'restaurant']

    def validate(self, attrs):
        user = self.context['request'].user
        restaurant_data = attrs.pop('restaurant')
        restaurants = Restaurant.objects.filter(id__in=restaurant_data)
        for restaurant in restaurants:
            if user not in restaurant.chain.organization.authors.all():
                raise serializers.ValidationError('You are not an author of this restaurant')

        return attrs


class AddRestaurantToCategorySerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    def validate(self, attrs):
        user = self.context['request'].user
        category = Category.objects.filter(id=attrs.get('category_id')).first()
        restaurant = Restaurant.objects.filter(id=attrs.get('restaurant_id')).first()

        if category is None:
            raise serializers.ValidationError('Category not found')

        if restaurant is None:
            raise serializers.ValidationError('Restaurant not found')

        if user not in restaurant.chain.organization.authors.all():
            raise serializers.ValidationError('You are not an author of this restaurant')

        if restaurant in category.restaurant.all():
            raise serializers.ValidationError('Restaurant already in category')

        return attrs

    def create(self, validated_data):
        category = Category.objects.get(id=validated_data.get('category_id'))
        restaurant = Restaurant.objects.get(id=validated_data.get('restaurant_id'))

        category.restaurant.add(restaurant)

        return category



class GetKitchenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kitchen
        fields = '__all__'
