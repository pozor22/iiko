import random
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=True)
    code = models.IntegerField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.code:
            while True:
                self.code = random.randint(100000, 999999)
                if not User.objects.filter(code=self.code).exists():
                    break
        super().save(*args, **kwargs)


class PasswordChangeConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="password_change_confirmation")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_confirmation_code(self):
        from django.utils.timezone import now
        self.code = f'{random.randint(100000, 999999)}'
        self.created_at = now()
        self.save()

    def is_code_valid(self):
        from datetime import timedelta
        from django.utils.timezone import now
        return now() - self.created_at <= timedelta(minutes=10)
