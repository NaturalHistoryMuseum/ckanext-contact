import pytest
from ckan.plugins import toolkit
from ckan.tests import factories
from ckanext.contact.auth import send_contact
from mock import MagicMock


def test_auth_always_succeeds_direct():
    assert send_contact(MagicMock(), MagicMock()) == {u'success': True}


@pytest.mark.ckan_config(u'ckan.plugins', u'contact')
@pytest.mark.usefixtures(u'with_plugins')
def test_auth_always_succeeds_anonymous():
    assert toolkit.check_access(u'send_contact', {})


@pytest.mark.ckan_config(u'ckan.plugins', u'contact')
@pytest.mark.usefixtures(u'with_plugins', u'clean_db')
def test_auth_always_succeeds_with_user():
    user = factories.User()
    assert toolkit.check_access(u'send_contact', {'user': user[u'name']})
