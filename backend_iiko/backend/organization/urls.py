from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'organization', views.OrganizationViewSet)
router.register(r'chain', views.ChainViewSet)


urlpatterns = [
    path('', include(router.urls)),
]