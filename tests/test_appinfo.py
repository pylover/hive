from bddrest import status, response

from .conftest import RESTAPITestCase
from hive import __version__ as appversion
from hive.models import User, Item


class TestApplicationInfo(RESTAPITestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        oscar = User(id='oscar', email='oscar@example.com', password='12345')
        franz = User(id='franz', email='franz@example.com', password='12345')
        oscar.items.append(Item(
            list='foo',
            title='bar'
        ))
        franz.items.append(Item(
            list='quux',
            title='baz'
        ))
        session.add(oscar)
        session.add(franz)
        session.commit()

    def test_info_anonymous(self):
        with self.given(
            'Getting the application information by an anonymous',
            verb='INFO'
        ):
            assert status == 401

    def test_info_authenticated(self):
        self.login('oscar@example.com', '12345')
        with self.given(
            'Getting the application information by an authenticated user',
            verb='INFO'
        ):

            assert status == '200 OK'
            assert response.text == \
f'''\
Shared Lists v{appversion}
Total Lists: 2
Total Users: 2
My Lists: 1
My Items: 1
'''

