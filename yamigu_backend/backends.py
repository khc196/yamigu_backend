from firebase_admin import auth
from authorization.models import User


class FirebaseBackend:
    def authenticate(self, request, uid=None):
        try:
            auth.get_user(uid)
            return User.objects.get(uid=uid)
        except User.DoesNotExist:
            return User.objects.create(uid=uid)
        except (auth.AuthError, ValueError):
            return None
