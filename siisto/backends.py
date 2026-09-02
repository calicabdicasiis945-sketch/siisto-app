from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authenticates against User model using either username or email (case-insensitive).
    Robustly checks all matching accounts and verifies active status.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        clean_input = str(username).strip()
        if not clean_input:
            return None

        try:
            # Check matching by username (case-insensitive)
            candidate_users = list(User.objects.filter(username__iexact=clean_input))

            # If input contains '@' or no username matched, search by email
            if '@' in clean_input or not candidate_users:
                email_users = list(User.objects.filter(email__iexact=clean_input).exclude(email=''))
                for eu in email_users:
                    if eu not in candidate_users:
                        candidate_users.append(eu)

            # Check password and active status for each candidate
            for user in candidate_users:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user

        except Exception:
            return None

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
