from django.contrib import admin

from .models import Category, Kitchen, Ingredient


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_restaurant')
    list_filter = ('restaurant',)
    search_fields = ('name',)

    def get_restaurant(self, obj):
        return ', '.join([restaurant.name for restaurant in obj.restaurant.all()])
    get_restaurant.short_description = 'Restaurant'


class KitchenAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_restaurant')
    list_filter = ('restaurant',)
    search_fields = ('name',)

    def get_restaurant(self, obj):
        return ', '.join([restaurant.name for restaurant in obj.restaurant.all()])
    get_restaurant.short_description = 'Restaurant'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'count', 'unit', 'chain')
    list_filter = ('chain',)
    search_fields = ('name',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Kitchen, KitchenAdmin)
admin.site.register(Ingredient, IngredientAdmin)
