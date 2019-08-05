from sqlalchemy import func
from nanohttp import text, HTTPBadRequest, context, HTTPNotFound, HTTPForbidden
from restfulpy.controllers import RestController
from restfulpy.orm import DBSession, commit
from restfulpy.authorization import authorize

from .models import User, Item


CR = '\n'


class Root(RestController):

    @classmethod
    def _get_current_user(cls):
        if not hasattr(context, 'identity') or context.identity is None:
            return None

        principal = context.identity
        return DBSession.query(User) \
            .filter(User.id == principal.payload.get('id')) \
            .one_or_none()

    @classmethod
    def _get_all_items(cls):
        query = DBSession.query(Item) \
            .filter(Item.ownerid == context.identity.id) \
            .order_by(Item.ownerid, Item.list, Item.title)

        return [f'{i.list}/{i.title}{CR}' for i in query]

    @classmethod
    def _get_items(cls, listtitle):
        query = DBSession.query(Item) \
            .filter(Item.ownerid == context.identity.id) \
            .filter(Item.list == listtitle) \
            .order_by(Item.id)

        return [f'{i.title}{CR}' for i in query]

    @classmethod
    def _get_lists(cls):
        query = DBSession \
            .query(Item.list) \
            .filter(Item.ownerid == context.identity.id) \
            .group_by(Item.list) \
            .order_by(Item.list)

        if not query.count():
            return ''

        return [f'{l[0]}{CR}' for l in query]

    @text
    @authorize
    def info(self):
        from hive import __version__ as appversion

        users = DBSession.query(User).count()
        lists = DBSession.query(Item.ownerid, Item.list) \
            .group_by(Item.ownerid, Item.list).count()

        result = [
            f'Shared Lists v{appversion}',
            f'Total Lists: {lists}',
            f'Total Users: {users}',
        ]

        me = context.identity.id
        mylists = DBSession.query(Item.ownerid, Item.list) \
            .filter(Item.ownerid == me) \
            .group_by(Item.ownerid, Item.list) \
            .count()
        myitems = DBSession.query(Item.ownerid, Item.list) \
            .filter(Item.ownerid == me) \
            .count()
        result.append(f'My Lists: {mylists}')
        result.append(f'My Items: {myitems}')

        result.append('')
        return CR.join(result)

    @text
    def login(self):
        email = context.form.get('email')
        password = context.form.get('password')

        def bad():
            raise HTTPBadRequest('Invalid email or password')

        if not (email and password):
            bad()

        principal = context.application \
            .__authenticator__ \
            .login((email, password))

        if principal is None:
            bad()

        return principal.dump()

    @text
    @authorize
    @commit
    def append(self, listtitle, itemtitle):
        me = self._get_current_user()
        item = Item(
            ownerid=context.identity.id,
            list=listtitle,
            title=itemtitle
        )
        me.items.append(item)
        DBSession.flush()
        return ''.join((str(item), CR))

    @text
    @authorize
    @commit
    def delete(self, listtitle, itemtitle):
        me = context.identity.id
        item = DBSession.query(Item) \
            .filter(Item.ownerid == me) \
            .filter(Item.list == listtitle) \
            .filter(Item.title == itemtitle) \
            .one_or_none()

        if item is None:
            raise HTTPNotFound()

        DBSession.delete(item)
        return ''.join((str(item), CR))

    @text
    @authorize
    def get(self, listtitle=None):
        if listtitle == 'all':
            return self._get_all_items()

        if listtitle:
            return self._get_items(listtitle)

        return self._get_lists()

