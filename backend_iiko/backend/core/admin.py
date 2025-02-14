from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import User

admin.site.register(User)
admin.site.register(Permission)
