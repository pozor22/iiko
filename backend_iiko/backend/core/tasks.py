from celery import shared_task
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.conf import settings

from .models import User


@shared_task
def send_email_active_account(user_id):
    try:
        user = User.objects.get(id=user_id)

        mail_subject = 'Подтвердите ваш аккаунт'
        message = render_to_string('core/email_verification.html', {
            'user': user,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        send_mail(
            mail_subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        pass


@shared_task
def send_email_code(user_id, code):
    try:
        user = User.objects.get(id=user_id)

        mail_subject = 'Подтвердите смену пароля'
        message = render_to_string('core/email_code.html', {
            'user': user,
            'code': code,
        })
        send_mail(
            mail_subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        print(f"User with id {user_id} does not exist")
