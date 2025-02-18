from django.urls import path

from . import views


urlpatterns = [
    path('registration/', views.create_user, name='registration'),
    path('login/', views.login_user, name='login'),
    path('login_code/', views.login_user_with_code, name='login_code'),
    path('self_user/', views.get_self_user, name='users'),
    path('confirm_email/<str:uidb64>/<str:token>/', views.email_confirmed, name='confirm_email'),
    path('chan_us_em/', views.change_username, name='chan_us_em'),
]
