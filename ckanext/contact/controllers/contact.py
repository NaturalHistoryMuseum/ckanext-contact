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
flatten_to_string_key = logic.flatten_to_string_key


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
        data_dict = logic.clean_dict(unflatten(logic.tuplize_dict(logic.parse_params(
            request.params))))

        try:
            recaptcha.check_recaptcha(data_dict.get(u'g-recaptcha-response', None),
                                      self.expected_action)
        except recaptcha.RecaptchaError as e:
            log.info(u'Recaptcha failed due to "{}"'.format(e))
            error_msg = _(u'Recaptcha failed, please try again.')
            h.flash_error(error_msg)
            return data_dict, errors, error_summary

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
                mailer.mail_recipient(**mail_dict)
            except (mailer.MailerException, socket.error):
                h.flash_error(
                    _(u'Sorry, there was an error sending the email. Please try again later'))
            else:
                data_dict['success'] = True

        return data_dict, errors, error_summary

    def ajax_submit(self):
        """
        AJAX form submission
        @return:
        """
        data, errors, error_summary = self._submit()
        data = flatten_to_string_key(
            {'data': data, 'errors': errors, 'error_summary': error_summary})
        response.headers['Content-Type'] = 'application/json;charset=utf-8'
        return h.json.dumps(data)

    def form(self):
        """
        Return a contact form
        :return: html
        """
        data = {}
        errors = {}
        error_summary = {}

        # Submit the data
        if request.method == u'POST':
            data, errors, error_summary = self._submit()
        else:
            # Try and use logged in user values for default values
            try:
                data['name'] = base.c.userobj.fullname or base.c.userobj.name
                data['email'] = base.c.userobj.email
            except AttributeError:
                data['name'] = data['email'] = None

        if data.get('success', False):
            return p.toolkit.render('contact/success.html')
        else:
            extra_vars = {
                'data': data,
                'errors': errors,
                'error_summary': error_summary,
                'recaptcha_v3_key': config.get('ckanext.contact.recaptcha_v3_key'),
                'recaptcha_v3_action': config.get('ckanext.contact.recaptcha_v3_action'),
            }
            return p.toolkit.render('contact/form.html', extra_vars=extra_vars)
