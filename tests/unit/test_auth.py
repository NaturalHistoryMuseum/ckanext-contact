import pytest
from ckan.plugins import toolkit
from ckan.tests import factories
from ckanext.contact.auth import send_contact
from mock import MagicMock


def test_auth_always_succeeds_direct():
    assert send_contact(MagicMock(), MagicMock()) == {'success': True}


@pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
@pytest.mark.ckan_config('ckan.plugins', 'contact')
@pytest.mark.usefixtures('with_plugins')
def test_auth_always_succeeds_anonymous():
    assert toolkit.check_access('send_contact', {})


@pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
@pytest.mark.ckan_config('ckan.plugins', 'contact')
@pytest.mark.usefixtures('with_plugins', 'clean_db')
def test_auth_always_succeeds_with_user():
    user = factories.User()
    assert toolkit.check_access('send_contact', {'user': user['name']})
