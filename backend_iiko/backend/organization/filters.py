import django_filters

from .models import Chain, Organization, Restaurant


class OrganizationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    my_organization = django_filters.BooleanFilter(method='filter_my_organization')
    me_in_organization = django_filters.BooleanFilter(method='filter_me_in_organization')

    class Meta:
        model = Organization
        fields = ['name', 'my_organization', 'me_in_organization']

    def filter_my_organization(self, queryset, name, value):
        user = self.request.user

        if value:
            return queryset.filter(authors=user)

        return queryset

    def filter_me_in_organization(self, queryset, name, value):
        user = self.request.user

        if value:
            return user.organizations.all()

        return queryset


class ChainFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    my_chain = django_filters.BooleanFilter(method='filter_my_chain')
    me_in_chain = django_filters.BooleanFilter(method='filter_me_in_chain')

    class Meta:
        model = Chain
        fields = ['name', 'my_chain', 'me_in_chain']

    def filter_my_chain(self, queryset, name, value):
        user = self.request.user

        if value:
            return queryset.filter(organization__authors=user)

        return queryset

    def filter_me_in_chain(self, queryset, name, value):
        user = self.request.user

        if value:
            return user.chains.all()

        return queryset


class RestaurantFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    my_restaurant = django_filters.BooleanFilter(method='filter_my_restaurant')
    me_in_restaurant = django_filters.BooleanFilter(method='filter_me_in_restaurant')

    class Meta:
        model = Restaurant
        fields = ['name', 'my_restaurant', 'me_in_restaurant']

    def filter_my_restaurant(self, queryset, name, value):
        user = self.request.user

        if value:
            return queryset.filter(chain__organization__authors=user)

        return queryset

    def filter_me_in_restaurant(self, queryset, name, value):
        user = self.request.user

        if value:
            return user.restaurants.all()

        return queryset
