from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'category', views.CategoryViewSet)
router.register(r'kitchen', views.KitchenViewSet)


urlpatterns = [
    path('', include(router.urls)),
]