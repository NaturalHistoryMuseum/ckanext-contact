#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-contact
# Created by the Natural History Museum in London, UK

import logging
import socket

from ckanext.contact.interfaces import IContact

from ckan import logic
from ckan.lib import captcha, mailer
from ckan.plugins import PluginImplementations, toolkit

log = logging.getLogger(__name__)


class ContactController(toolkit.BaseController):
    '''Controller for displaying a contact form'''

    def __before__(self, action, **env):

        super(ContactController, self).__before__(action, **env)

        try:
            self.context = {
                u'user': toolkit.c.user or toolkit.c.author,
                }
            toolkit.check_access(u'send_contact', self.context)
        except toolkit.NotAuthorized:
            toolkit.abort(401, toolkit._(u'Not authorized to use contact form'))

    @staticmethod
    def _submit(context):
        '''

        :param context: 

        '''

        try:
            data_dict = logic.clean_dict(
                toolkit.dictization_functions.unflatten(
                    logic.tuplize_dict(logic.parse_params(toolkit.request.params))))
            context[u'message'] = data_dict.get(u'log_message', u'')
            toolkit.c.form = data_dict[u'name']
            captcha.check_recaptcha(toolkit.request)
        except logic.NotAuthorized:
            toolkit.abort(401, toolkit._(u'Not authorized to see this page'))
        except captcha.CaptchaError:
            error_msg = toolkit._(u'Bad Captcha. Please try again.')
            toolkit.h.flash_error(error_msg)

        errors = {}
        error_summary = {}

        if data_dict[u'email'] == u'':
            errors[u'email'] = [u'Missing Value']
            error_summary[u'email'] = u'Missing value'

        if data_dict[u'name'] == u'':
            errors[u'name'] = [u'Missing Value']
            error_summary[u'name'] = u'Missing value'

        if data_dict[u'content'] == u'':
            errors[u'content'] = [u'Missing Value']
            error_summary[u'content'] = u'Missing value'

        if len(errors) == 0:

            body = u'%s' % data_dict[u'content']
            body += u'\n\nSent by:\nName:%s\nEmail: %s\n' % (
                data_dict[u'name'], data_dict[u'email'])
            mail_dict = {
                u'recipient_email': toolkit.config.get(u'ckanext.contact.mail_to',
                                                       toolkit.config.get(u'email_to')),
                u'recipient_name': toolkit.config.get(u'ckanext.contact.recipient_name',
                                                      toolkit.config.get(
                                                          u'ckan.site_title')),
                u'subject': toolkit.config.get(u'ckanext.contact.subject',
                                               u'Contact/Question from visitor'),
                u'body': body,
                u'headers': {
                    u'reply-to': data_dict[u'email']
                    }
                }

            # Allow other plugins to modify the mail_dict
            for plugin in PluginImplementations(IContact):
                plugin.mail_alter(mail_dict, data_dict)

            try:
                mailer.mail_recipient(**mail_dict)
            except (mailer.MailerException, socket.error):
                toolkit.h.flash_error(toolkit._(
                    u'Sorry, there was an error sending the email. Please try again later'))
            else:
                data_dict[u'success'] = True

        return data_dict, errors, error_summary

    def ajax_submit(self):
        '''AJAX form submission'''
        data, errors, error_summary = self._submit(self.context)
        data = logic.flatten_to_string_key({
            u'data': data,
            u'errors': errors,
            u'error_summary': error_summary
            })
        toolkit.response.headers[u'Content-Type'] = u'application/json;charset=utf-8'
        return toolkit.h.json.dumps(data)

    def form(self):

        '''


        :returns: :return: html

        '''

        data = {}
        errors = {}
        error_summary = {}

        # Submit the data
        if u'save' in toolkit.request.params:
            data, errors, error_summary = self._submit(self.context)
        else:
            # Try and use logged in user values for default values
            try:
                data[u'name'] = toolkit.c.userobj.fullname or toolkit.c.userobj.name
                data[u'email'] = toolkit.c.userobj.email
            except AttributeError:
                data[u'name'] = data[u'email'] = None

        if data.get(u'success', False):
            return toolkit.render(u'contact/success.html')
        else:
            vars = {
                u'data': data,
                u'errors': errors,
                u'error_summary': error_summary
                }
            return toolkit.render(u'contact/form.html', extra_vars=vars)
