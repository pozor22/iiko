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
