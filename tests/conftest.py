from os import path

from restfulpy.testing import ApplicableTestCase
from restfulpy.principal import JWTPrincipal

from hive import SharedLists
from hive.models import User


HERE = path.abspath(path.dirname(__file__))
DATA_DIRECTORY = path.abspath(path.join(HERE, '../../data'))


class RESTAPITestCase(ApplicableTestCase):
    __application__ = SharedLists()
    __story_directory__ = path.join(DATA_DIRECTORY, 'stories')
    __api_documentation_directory__ = path.join(DATA_DIRECTORY, 'markdown')
    __metadata__ = {
        #r'^/lists.*': List.json_metadata()['fields']
    }

    def login(self, email, password):
        with self.given(
                None,
                '/',
                'LOGIN',
                form=dict(email=email, password=password),
        ) as story:
            response = story.response
            assert response.status == '200 OK'
            self._authentication_token = response.text

