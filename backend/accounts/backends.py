from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None or password is None:
            return None
        User = get_user_model()
        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            User().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user) and not user.is_deleted:
            return user
        return None


class UsernameBackend(ModelBackend):
    """Allow named administrator accounts without requiring an invented phone."""
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        User = get_user_model()
        try:
            user = User.objects.get(username=username, is_staff=True)
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user) and not user.is_deleted:
            return user
        return None
