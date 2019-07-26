#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-contact
# Created by the Natural History Museum in London, UK

import json
import logging
import socket

from ckanext.contact import recaptcha
from ckanext.contact.interfaces import IContact

from ckan import logic
from ckan.lib import mailer
from ckan.plugins import PluginImplementations, toolkit

log = logging.getLogger(__name__)


class ContactController(toolkit.BaseController):
    '''
    Controller for displaying a contact form
    '''

    def __before__(self, action, **env):
        '''
        This function runs before the request handler to setup a few things. We use it to set the
        context dict and the user has check access.

        :param action: the action the user is attempting to perform (i.e. the handler)
        :param env: the environment object
        '''
        super(ContactController, self).__before__(action, **env)

        try:
            self.context = {
                u'user': toolkit.c.user or toolkit.c.author
                }
            toolkit.check_access(u'send_contact', self.context)
        except toolkit.NotAuthorized:
            toolkit.abort(401, toolkit._(u'Not authorized to use contact form'))

        self.expected_action = toolkit.config.get(u'ckanext.contact.recaptcha_v3_action')

    def _validate(self, data_dict):
        '''
        Validates the given data and recaptcha if necessary.

        :param data_dict: the request params as a dict
        :return: a 3-tuple of errors, error summaries and a recaptcha error, in the event where no
                 issues occur the return is ({}, {}, None)
        '''
        errors = {}
        error_summary = {}
        recaptcha_error = None

        # check the three fields we know about
        for field in (u'email', u'name', u'content'):
            value = data_dict.get(field, None)
            if value is None or value == u'':
                errors[field] = [u'Missing Value']
                error_summary[field] = u'Missing value'

        # only check the recaptcha if there are no errors
        if not errors:
            try:
                # check the recaptcha value, this only does anything if recaptcha is setup
                recaptcha.check_recaptcha(data_dict.get(u'g-recaptcha-response', None),
                                          self.expected_action)
            except recaptcha.RecaptchaError as e:
                log.info(u'Recaptcha failed due to "{}"'.format(e))
                recaptcha_error = toolkit._(u'Recaptcha check failed, please try again.')

        return errors, error_summary, recaptcha_error

    def _submit(self):
        '''
        Take the data in the request params and send an email using them. If the data is invalid or
        a recaptcha is setup and it fails, don't send the email.

        :return: a dict of details
        '''
        # this variable holds the status of sending the email
        email_success = True

        # pull out the data from the request
        data_dict = logic.clean_dict(
            toolkit.dictization_functions.unflatten(logic.tuplize_dict(logic.parse_params(
                toolkit.request.params))))

        # validate the request params
        errors, error_summary, recaptcha_error = self._validate(data_dict)

        # if there are not errors and no recaptcha error, attempt to send the email
        if len(errors) == 0 and recaptcha_error is None:
            body = u'{}\n\nSent by:\nName: {}\nEmail: {}\n'.format(data_dict[u'content'],
                                                                   data_dict[u'name'],
                                                                   data_dict[u'email'])
            mail_dict = {
                u'recipient_email': toolkit.config.get(u'ckanext.contact.mail_to',
                                                       toolkit.config.get(u'email_to')),
                u'recipient_name': toolkit.config.get(u'ckanext.contact.recipient_name',
                                                      toolkit.config.get(u'ckan.site_title')),
                u'subject': toolkit.config.get(u'ckanext.contact.subject',
                                               toolkit._(u'Contact/Question from visitor')),
                u'body': body,
                u'headers': {
                    u'reply-to': data_dict[u'email']
                    }
                }

            # allow other plugins to modify the mail_dict
            for plugin in PluginImplementations(IContact):
                plugin.mail_alter(mail_dict, data_dict)

            try:
                mailer.mail_recipient(**mail_dict)
            except (mailer.MailerException, socket.error):
                email_success = False

        return {
            u'success': recaptcha_error is None and len(errors) == 0 and email_success,
            u'data': data_dict,
            u'errors': errors,
            u'error_summary': error_summary,
            u'recaptcha_error': recaptcha_error,
            }

    def ajax_submit(self):
        '''
        AJAX form submission.

        :return: json dumped data for the response
        '''
        toolkit.response.headers[b'Content-Type'] = b'application/json;charset=utf-8'
        return json.dumps(self._submit())

    def form(self):
        '''
        Form based interaction, if called as a POST request the request params are used to send the
        email, if not then the form template is rendered.

        :return: a page, either the form page or the success page if the email was sent successfully
        '''
        # dict of context values for the template renderer
        extra_vars = {
            u'data': {},
            u'errors': {},
            u'error_summary': {},
            }

        if toolkit.request.method == u'POST':
            result = self._submit()
            if result.get(u'success', False):
                return toolkit.render(u'contact/success.html')
            else:
                # the form page isn't setup to handle this error so we need to flash it here for it
                if result[u'recaptcha_error'] is not None:
                    toolkit.h.flash_error(result[u'recaptcha_error'])
                # note that this copies over an recaptcha error key/value present in the submit
                # result
                extra_vars.update(result)
        else:
            # try and use logged in user values for default values
            try:
                extra_vars[u'data'][u'name'] = toolkit.c.userobj.fullname or toolkit.c.userobj.name
                extra_vars[u'data'][u'email'] = toolkit.c.userobj.email
            except AttributeError:
                extra_vars[u'data'][u'name'] = extra_vars[u'data'][u'email'] = None

        return toolkit.render(u'contact/form.html', extra_vars=extra_vars)
