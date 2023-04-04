import pytest
from datetime import datetime, timezone

from ckanext.contact.routes._helpers import build_subject
from freezegun import freeze_time


class TestBuildSubject:
    def test_no_config_all_defaults(self):
        subject = build_subject()
        assert subject == 'Contact/Question from visitor'

    def test_no_config_pass_default_subject(self):
        default = 'TEST SUBJECT'

        subject = build_subject(default=default)
        assert subject == default

    def test_user_specified(self):
        subject = 'YES PLEASE EMAIL'
        assert build_subject(subject=subject) == subject

    @pytest.mark.ckan_config('ckanext.contact.subject', 'TEST SUBJECT')
    def test_user_specified_and_defaults(self):
        subject = 'YES PLEASE EMAIL'

        assert build_subject(subject=subject) == subject

    def test_no_config_pass_default_timestamp_false(self):
        timestamp_default = False

        subject = build_subject(timestamp_default=timestamp_default)
        assert subject == 'Contact/Question from visitor'

    @freeze_time("2021-01-01")
    def test_no_config_pass_default_timestamp_true(self):
        timestamp_default = True

        subject = build_subject(timestamp_default=timestamp_default)

        timestamp = datetime(2021, 1, 1, tzinfo=timezone.utc).strftime(
            '%Y-%m-%d %H:%M:%S %Z'
        )
        assert subject == f'Contact/Question from visitor [{timestamp}]'

    @freeze_time("2021-01-01")
    def test_no_config_pass_both(self):
        subject_default = 'TEST SUBJECT'
        timestamp_default = True

        subject = build_subject(
            default=subject_default, timestamp_default=timestamp_default
        )

        timestamp = datetime(2021, 1, 1, tzinfo=timezone.utc).strftime(
            '%Y-%m-%d %H:%M:%S %Z'
        )
        assert subject == f'{subject_default} [{timestamp}]'

    @freeze_time("2021-01-01")
    @pytest.mark.ckan_config('ckanext.contact.subject', 'TEST SUBJECT')
    @pytest.mark.ckan_config('ckanext.contact.add_timestamp_to_subject', 'true')
    def test_config_with_timestamp(self):
        subject = build_subject()

        timestamp = datetime(2021, 1, 1, tzinfo=timezone.utc).strftime(
            '%Y-%m-%d %H:%M:%S %Z'
        )
        assert subject == f'TEST SUBJECT [{timestamp}]'

    @pytest.mark.ckan_config('ckanext.contact.subject', 'TEST SUBJECT')
    @pytest.mark.ckan_config('ckanext.contact.add_timestamp_to_subject', 'false')
    def test_config_with_timestamp(self):
        subject = build_subject()
        assert subject == 'TEST SUBJECT'

    def test_prefix_not_provided(self):
        subject = build_subject(subject='TEST')
        assert subject == 'TEST'

    @pytest.mark.ckan_config('ckanext.contact.subject_prefix', 'PREFIX:')
    def test_prefix_provided(self):
        subject = build_subject(subject='TEST')
        assert subject == 'PREFIX: TEST'
