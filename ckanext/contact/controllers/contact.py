import json
import logging

import socket
from pylons import config

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.mailer as mailer
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.logic as logic
import ckan.model as model
import ckan.plugins as p
from ckan.common import _, request, response
from ckanext.contact import recaptcha
from ckanext.contact.interfaces import IContact

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

DataError = dictization_functions.DataError
unflatten = dictization_functions.unflatten

check_access = logic.check_access
get_action = logic.get_action


class ContactController(base.BaseController):
    """
    Controller for displaying a contact form
    """

    def __before__(self, action, **env):
        super(ContactController, self).__before__(action, **env)

        try:
            self.context = {
                'model': model,
                'session': model.Session,
                'user': base.c.user or base.c.author,
                'auth_user_obj': base.c.userobj
            }
            check_access('send_contact', self.context)
        except logic.NotAuthorized:
            base.abort(401, _('Not authorized to use contact form'))

        self.expected_action = config.get(u'ckanext.contact.recaptcha_v3_action')

    def _submit(self):
        errors = {}
        error_summary = {}
        recaptcha_error = None

        data_dict = logic.clean_dict(unflatten(logic.tuplize_dict(logic.parse_params(
            request.params))))

        if data_dict["email"] == '':
            errors['email'] = [u'Missing Value']
            error_summary['email'] = u'Missing value'

        if data_dict["name"] == '':
            errors['name'] = [u'Missing Value']
            error_summary['name'] = u'Missing value'

        if data_dict["content"] == '':
            errors['content'] = [u'Missing Value']
            error_summary['content'] = u'Missing value'

        if len(errors) == 0:
            try:
                recaptcha.check_recaptcha(data_dict.get(u'g-recaptcha-response', None),
                                          self.expected_action)
            except recaptcha.RecaptchaError as e:
                log.info(u'Recaptcha failed due to "{}"'.format(e))
                recaptcha_error = _(u'Recaptcha check failed, please try again.')

            if recaptcha_error is None:
                body = '%s' % data_dict["content"]
                body += '\n\nSent by:\nName:%s\nEmail: %s\n' % (data_dict["name"], data_dict["email"])
                mail_dict = {
                    'recipient_email': config.get("ckanext.contact.mail_to", config.get('email_to')),
                    'recipient_name': config.get("ckanext.contact.recipient_name",
                                                 config.get('ckan.site_title')),
                    'subject': config.get("ckanext.contact.subject", 'Contact/Question from visitor'),
                    'body': body,
                    'headers': {'reply-to': data_dict["email"]}
                }

                # Allow other plugins to modify the mail_dict
                for plugin in p.PluginImplementations(IContact):
                    plugin.mail_alter(mail_dict, data_dict)

                try:
                    pass
                    # mailer.mail_recipient(**mail_dict)
                except (mailer.MailerException, socket.error):
                    h.flash_error(
                        _(u'Sorry, there was an error sending the email. Please try again later'))

        return {
            u'success': recaptcha_error is None and len(errors) == 0,
            u'data': data_dict,
            u'errors': errors,
            u'error_summary': error_summary,
            u'recaptcha_error': recaptcha_error,
        }

    def ajax_submit(self):
        """
        AJAX form submission
        @return:
        """
        response.headers['Content-Type'] = 'application/json;charset=utf-8'
        return json.dumps(self._submit())

    def form(self):
        """
        Return a contact form
        :return: html
        """
        extra_vars = {
            u'data': {},
            u'errors': {},
            u'error_summary': {},
        }

        # submit the data
        if request.method == u'POST':
            result = self._submit()
            if result.get(u'success', False):
                return p.toolkit.render(u'contact/success.html')
            else:
                if result[u'recaptcha_error'] is not None:
                    h.flash_error(result[u'recaptcha_error'])
                # note that this copies over an recaptcha error key/value present in the submit
                # result
                extra_vars.update(result)
        else:
            # try and use logged in user values for default values
            try:
                extra_vars[u'data'][u'name'] = base.c.userobj.fullname or base.c.userobj.name
                extra_vars[u'data'][u'email'] = base.c.userobj.email
            except AttributeError:
                extra_vars[u'data'][u'name'] = extra_vars[u'data'][u'email'] = None

        return p.toolkit.render(u'contact/form.html', extra_vars=extra_vars)
