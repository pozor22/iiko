from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import User


class OrganizationInline(admin.TabularInline):
    model = User.organizations.through
    extra = 1


class ChainInline(admin.TabularInline):
    model = User.chains.through
    extra = 1


class RestaurantInline(admin.TabularInline):
    model = User.restaurants.through
    extra = 1


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'get_organization', 'get_chain', 'get_restaurant')
    list_filter = ('organizations', 'chains', 'restaurants')
    search_fields = ('email', 'username', 'code')
    ordering = ('id',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Дополнительная информация', {'fields': ('code',)}),
        ('Группы и права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )

    inlines = [OrganizationInline, ChainInline, RestaurantInline]

    filter_horizontal = ('organizations', 'chains', 'restaurants', 'groups', 'user_permissions')

    def get_organization(self, obj):
        return ', '.join([organization.name for organization in obj.organizations.all()])
    get_organization.short_description = 'Организации'

    def get_chain(self, obj):
        return ', '.join([chain.name for chain in obj.chains.all()])
    get_chain.short_description = 'Сети'

    def get_restaurant(self, obj):
        return ', '.join([restaurant.name for restaurant in obj.restaurants.all()])
    get_restaurant.short_description = 'Рестораны'


admin.site.register(User, UserAdmin)
admin.site.register(Permission)
