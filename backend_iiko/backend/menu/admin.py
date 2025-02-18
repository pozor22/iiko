from django.contrib import admin

from .models import Category, Kitchen, Product

admin.site.register(Category)
admin.site.register(Kitchen)
admin.site.register(Product)
