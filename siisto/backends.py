from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL using either username or email (case-insensitive).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        clean_username = str(username).strip()
        try:
            user = User.objects.filter(
                Q(username__iexact=clean_username) | Q(email__iexact=clean_username)
            ).first()
            if user and user.check_password(password):
                return user
        except Exception:
            return None
        return None
