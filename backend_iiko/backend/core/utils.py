from .models import User
from django.contrib.auth.backends import BaseBackend

class CodeAuthenticationBackend(BaseBackend):
    def authenticate(self, request, code=None):
        try:
            user = User.objects.get(code=code)
            if user is not None:
                return user
        except User.DoesNotExist:
            return None
