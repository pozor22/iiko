from django.contrib import admin

from .models import Organization, Chain, Restaurant

admin.site.register(Organization)
admin.site.register(Chain)
admin.site.register(Restaurant)
