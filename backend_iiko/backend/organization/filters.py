import django_filters

from .models import Chain


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
