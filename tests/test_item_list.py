from bddrest import status, response, when

from .conftest import RESTAPITestCase
from hive.models import User, Item


class TestItemList(RESTAPITestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        oscar = User(id='oscar', email='oscar@example.com', password='12345')
        franz = User(id='franz', email='franz@example.com', password='12345')
        oscar.items.append(Item(list='foo', title='bar'))
        franz.items.append(Item(list='foo', title='baz'))
        oscar.items.append(Item(list='foo', title='qux'))
        oscar.items.append(Item(list='quux', title='quuz'))
        session.add(oscar)
        session.add(franz)
        session.commit()

    def test_item_list(self):
        self.login('oscar', '12345')
        with self.given('List items', '/foo'):
            assert status == 200
            assert response.text == \
f'''\
bar
qux
'''

        with self.given('List all items', '/all'):
            assert status == 200
            assert response.text == \
f'''\
foo/bar
foo/qux
quux/quuz
'''

