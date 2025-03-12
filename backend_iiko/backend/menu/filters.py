import django_filters

from .models import Category


class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    restaurant = django_filters.CharFilter(field_name='restaurant__name', lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['name', 'restaurant']
