import django_filters

from .models import User

class UserFilter(django_filters.FilterSet):
    role = django_filters.CharFilter(field_name='groups__name', lookup_expr='exact')
    organizations = django_filters.CharFilter(field_name='organizations__name', lookup_expr='icontains')
    chains = django_filters.CharFilter(field_name='chains__name', lookup_expr='icontains')
    restaurants = django_filters.CharFilter(field_name='restaurants__name', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['role', 'organizations', 'chains', 'restaurants']