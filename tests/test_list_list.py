from bddrest import status, response, when

from .conftest import RESTAPITestCase
from hive.models import User, Item


class TestListList(RESTAPITestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        oscar = User(id='oscar', email='oscar@example.com', password='12345')
        franz = User(id='franz', email='franz@example.com', password='12345')
        oscar.items.append(Item(list='foo', title='bar'))
        oscar.items.append(Item(list='quux', title='qux'))
        franz.items.append(Item(list='foo', title='baz'))
        session.add(oscar)
        session.add(franz)
        session.commit()

    def test_list_list(self):
        self.login('oscar', '12345')
        with self.given('List lists', '/'):
            assert status == 200
            assert response.text == \
f'''\
foo
quux
'''

            when('Invalid list name', '/invalid')
            assert status == 200
            assert response.text == ''

        self.login('franz', '12345')
        with self.given('List lists', '/'):
            assert status == 200
            assert response.text == \
f'''\
foo
'''

class TestListEmptyList(RESTAPITestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        oscar = User(id='oscar', email='oscar@example.com', password='12345')
        session.add(oscar)
        session.commit()

    def test_list_emptylist(self):
        self.login('oscar', '12345')
        with self.given('List lists', '/oscar'):
            assert status == 200
            assert response.text == ''
