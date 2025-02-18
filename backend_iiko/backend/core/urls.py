from django.urls import path

from . import views


urlpatterns = [
    # Users
    path('registration/', views.create_user, name='registration'),
    path('delete_user/', views.delete_user, name='delete_user'),
    path('users/', views.get_users, name='users'),

    # Auth
    path('login/', views.login_user, name='login'),
    path('login_code/', views.login_user_with_code, name='login_code'),
    path('refresh_token/', views.refresh_token, name='refresh_token'),

    # Change_user
    path('chan_us_em/', views.change_username_or_email, name='chan_us_em'),
    path('chan_pass/', views.change_password, name='chan_pass'),

    # Confirm
    path('confirm_email/<str:uidb64>/<str:token>/', views.email_confirmed, name='confirm_email'),
    path('confirm_pass', views.confirm_password_change, name='confirm_pass'),
    path('resend_code', views.resend_code, name='resend_code'),
]
