from restfulpy.authentication import StatefulAuthenticator
from restfulpy.orm import DBSession

from .models import User


class Authenticator(StatefulAuthenticator):

    @staticmethod
    def _get_user(condition):
        user = DBSession.query(User).filter(condition).one_or_none()
        return user

    def create_principal(self, user_id=None, session_id=None):
        user = self._get_user(User.id == user_id)
        principal = user.create_jwt_principal()
        return principal

    def create_refresh_principal(self, user_id=None):
        user = self._get_user(User.id == user_id)
        return user.create_refresh_principal()

    def validate_credentials(self, credentials):
        email, password = credentials
        q = DBSession.query(User)
        if '@' not in email:
            q = q.filter(User.id == email)
        else:
            q = q.filter(User.email == email)

        user = q.one_or_none()

        if user is None or not user.validate_password(password):
            return None

        return user

