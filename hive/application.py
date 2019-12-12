from os.path import dirname

from restfulpy import Application

from .controllers import Root
from .authentication import Authenticator
from .cli import UserCommand


class Hive(Application):
    __authenticator__ = Authenticator()
    __cli_arguments__ = [
        UserCommand
    ]

    def __init__(self, name='hive'):
        super().__init__(
            name,
            root=Root(),
            path_=dirname(__file__),
        )

    def insert_mockup(self, args=None):  # pragma: no cover
        from restfulpy.orm import DBSession
        from .models import User
        oscar = User(id='pylover', email='pylover@example.com', password='12345')
        DBSession.add(oscar)
        DBSession.commit()

