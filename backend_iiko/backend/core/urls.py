from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


# router = DefaultRouter()
# router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('registration/', views.create_user, name='registration'),
    path('login/', views.login_user, name='login'),
    path('users/', views.get_self_user, name='users'),
    path('confirm_email/<str:uidb64>/<str:token>/', views.get_self_user, name='confirm_email'),
]
