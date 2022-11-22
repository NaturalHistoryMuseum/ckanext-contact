# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-contact
# Created by the Natural History Museum in London, UK
import logging
import socket
from ckan import logic
from ckan.common import asbool
from ckan.lib import mailer
from ckan.lib.navl.dictization_functions import unflatten
from ckan.plugins import PluginImplementations, toolkit
from ckanext.contact import recaptcha
from ckanext.contact.interfaces import IContact
from datetime import datetime, timezone

log = logging.getLogger(__name__)


def validate(data_dict):
    """
    Validates the given data and recaptcha if necessary.

    :param data_dict: the request params as a dict
    :return: a 3-tuple of errors, error summaries and a recaptcha error, in the event where no
             issues occur the return is ({}, {}, None)
    """
    errors = {}
    error_summary = {}
    recaptcha_error = None

    # check each field to see if it has a value and if not, show and error
    for field, value in data_dict.items():
        # we know the save field is not necessary and may be empty so ignore it
        if field == 'save':
            continue
        if value is None or value == '':
            errors[field] = ['Missing Value']
            error_summary[field] = 'Missing value'

    # only check the recaptcha if there are no errors
    if not errors:
        try:
            expected_action = toolkit.config.get('ckanext.contact.recaptcha_v3_action')
            # check the recaptcha value, this only does anything if recaptcha is setup
            recaptcha.check_recaptcha(
                data_dict.get('g-recaptcha-response', None), expected_action
            )
        except recaptcha.RecaptchaError as e:
            log.info(f'Recaptcha failed due to "{e}"')
            recaptcha_error = toolkit._('Recaptcha check failed, please try again.')

    return errors, error_summary, recaptcha_error


def build_subject(
    subject_default='Contact/Question from visitor', timestamp_default=False
):
    """
    Creates the subject line for the contact email using the config or the defaults.

    :param subject_default: the default str to use if ckanext.contact.subject isn't specified
    :param timestamp_default: the default bool to use if add_timestamp_to_subject isn't specified
    :return: the subject line
    """
    subject = toolkit.config.get('ckanext.contact.subject', toolkit._(subject_default))
    if asbool(
        toolkit.config.get(
            'ckanext.contact.add_timestamp_to_subject', timestamp_default
        )
    ):
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
        subject = f'{subject} [{timestamp}]'
    return subject


def submit():
    """
    Take the data in the request params and send an email using them. If the data is
    invalid or a recaptcha is setup and it fails, don't send the email.

    :return: a dict of details
    """
    # this variable holds the status of sending the email
    email_success = True

    # pull out the data from the request
    data_dict = logic.clean_dict(
        unflatten(logic.tuplize_dict(logic.parse_params(toolkit.request.values)))
    )

    # validate the request params
    errors, error_summary, recaptcha_error = validate(data_dict)

    # if there are not errors and no recaptcha error, attempt to send the email
    if len(errors) == 0 and recaptcha_error is None:
        body_parts = [
            f'{data_dict["content"]}\n',
            'Sent by:',
            f'  Name: {data_dict["name"]}',
            f'  Email: {data_dict["email"]}',
        ]
        mail_dict = {
            'recipient_email': toolkit.config.get(
                'ckanext.contact.mail_to', toolkit.config.get('email_to')
            ),
            'recipient_name': toolkit.config.get(
                'ckanext.contact.recipient_name', toolkit.config.get('ckan.site_title')
            ),
            'subject': build_subject(),
            'body': '\n'.join(body_parts),
            'headers': {'reply-to': data_dict['email']},
        }

        # allow other plugins to modify the mail_dict
        for plugin in PluginImplementations(IContact):
            plugin.mail_alter(mail_dict, data_dict)

        try:
            mailer.mail_recipient(**mail_dict)
        except (mailer.MailerException, socket.error):
            email_success = False

    return {
        'success': recaptcha_error is None and len(errors) == 0 and email_success,
        'data': data_dict,
        'errors': errors,
        'error_summary': error_summary,
        'recaptcha_error': recaptcha_error,
    }
