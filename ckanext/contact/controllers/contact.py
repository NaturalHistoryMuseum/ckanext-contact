import logging
import ckan.plugins as p
import ckan.logic as logic
import ckan.model as model
import ckan.lib.captcha as captcha
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.lib.mailer as mailer

import ckan.plugins.toolkit as toolkit

import socket
from pylons import config
from ckanext.contact.interfaces import IContact

log = logging.getLogger(__name__)

render = toolkit.render
abort = toolkit.abort

DataError = dictization_functions.DataError
unflatten = dictization_functions.unflatten

check_access = toolkit.check_access
get_action = toolkit.get_action
flatten_to_string_key = logic.flatten_to_string_key


class ContactController(toolkit.BaseController):
    """
    Controller for displaying a contact form
    """

    def __before__(self, action, **env):

        super(ContactController, self).__before__(action, **env)

        try:
            self.context = {'model': model, 'session': model.Session,
                            'user': toolkit.c.user or toolkit.c.author,
                            'auth_user_obj': toolkit.c.userobj}
            check_access('send_contact', self.context)
        except logic.NotAuthorized:
            abort(401, toolkit._('Not authorized to use contact form'))

    @staticmethod
    def _submit(context):

        try:
            data_dict = \
                logic.clean_dict(unflatten(logic.tuplize_dict(
                                           logic.parse_params(
                                            toolkit.request.params))))
            context['message'] = data_dict.get('log_message', '')
            toolkit.c.form = data_dict['name']
            captcha.check_recaptcha(toolkit.request)
        except logic.NotAuthorized:
            abort(401, toolkit._('Not authorized to see this page'))
        except captcha.CaptchaError:
            error_msg = toolkit._(u'Bad Captcha. Please try again.')
            toolkit.h.flash_error(error_msg)

        errors = {}
        error_summary = {}

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
            body += '\n\nSent by:\nName:%s\nEmail: %s\n' % (data_dict["name"],
                                                            data_dict["email"])
            mail_dict = {
                'recipient_email': config.get("ckanext.contact.mail_to",
                                              config.get('email_to')),
                'recipient_name': config.get("ckanext.contact.recipient_name",
                                             config.get('ckan.site_title')),
                'subject': config.get("ckanext.contact.subject",
                                      'Contact/Question from visitor'),
                'body': body,
                'headers': {'reply-to': data_dict["email"]}
            }

            # Allow other plugins to modify the mail_dict
            for plugin in p.PluginImplementations(IContact):
                plugin.mail_alter(mail_dict, data_dict)

            try:
                mailer.mail_recipient(**mail_dict)
            except (mailer.MailerException, socket.error):
                toolkit.h.flash_error(
                    toolkit._(u'Sorry, there was an error sending the email. Please try again later'))
            else:
                data_dict['success'] = True

        return data_dict, errors, error_summary

    def ajax_submit(self):
        """
        AJAX form submission
        @return:
        """
        data, errors, error_summary = self._submit(self.context)
        data = flatten_to_string_key({'data': data, 'errors': errors,
                                      'error_summary': error_summary})
        toolkit.response.headers['Content-Type'] = \
            'application/json;charset=utf-8'
        return toolkit.h.json.dumps(data)

    def form(self):

        """
        Return a contact form
        :return: html
        """

        data = {}
        errors = {}
        error_summary = {}

        # Submit the data
        if 'save' in toolkit.request.params:
            data, errors, error_summary = self._submit(self.context)
        else:
            # Try and use logged in user values for default values
            try:
                data['name'] = \
                    toolkit.c.userobj.fullname or toolkit.c.userobj.name
                data['email'] = toolkit.c.userobj.email
            except AttributeError:
                data['name'] = data['email'] = None

        if data.get('success', False):
            return p.toolkit.render('contact/success.html')
        else:
            vars = {'data': data, 'errors': errors,
                    'error_summary': error_summary}
            return p.toolkit.render('contact/form.html', extra_vars=vars)
