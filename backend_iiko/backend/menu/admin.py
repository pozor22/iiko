from django.contrib import admin

from .models import Category, Kitchen, Product


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_restaurant')
    list_filter = ('restaurant',)
    search_fields = ('name',)

    def get_restaurant(self, obj):
        return ', '.join([restaurant.name for restaurant in obj.restaurant.all()])
    get_restaurant.short_description = 'Restaurant'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Kitchen)
admin.site.register(Product)
