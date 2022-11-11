# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-contact
# Created by the Natural History Museum in London, UK

import logging

from ckan.plugins import toolkit
from flask import Blueprint, jsonify

from . import _helpers

log = logging.getLogger(__name__)

blueprint = Blueprint(name='contact', import_name=__name__, url_prefix='/contact')


def _context():
    return {'user': toolkit.c.user or toolkit.c.author}


@blueprint.before_request
def before_request():
    """
    This function runs before the request handler to setup a few things. We use it to
    set the context dict and the user has check access.

    :param action: the action the user is attempting to perform (i.e. the handler)
    :param env: the environment object
    """

    try:
        toolkit.check_access('send_contact', _context())
    except toolkit.NotAuthorized:
        toolkit.abort(401, toolkit._('Not authorized to use contact form'))


@blueprint.route('', methods=['GET', 'POST'])
def form():
    """
    Form based interaction, if called as a POST request the request params are used to
    send the email, if not then the form template is rendered.

    :return: a page, either the form page or the success page if the email was sent successfully
    """
    # dict of context values for the template renderer
    extra_vars = {
        'data': {},
        'errors': {},
        'error_summary': {},
    }

    if toolkit.request.method == 'POST':
        result = _helpers.submit()
        if result.get('success', False):
            return toolkit.render('contact/success.html')
        else:
            # the form page isn't setup to handle this error so we need to flash it here for it
            if result['recaptcha_error'] is not None:
                toolkit.h.flash_error(result['recaptcha_error'])
            # note that this copies over an recaptcha error key/value present in the submit
            # result
            extra_vars.update(result)
    else:
        # try and use logged in user values for default values
        try:
            extra_vars['data']['name'] = (
                toolkit.c.userobj.fullname or toolkit.c.userobj.name
            )
            extra_vars['data']['email'] = toolkit.c.userobj.email
        except AttributeError:
            extra_vars['data']['name'] = extra_vars['data']['email'] = None

    return toolkit.render('contact/form.html', extra_vars=extra_vars)


@blueprint.route('/ajax', methods=['POST'])
def ajax_submit():
    """
    AJAX form submission.

    :return: json dumped data for the response
    """
    return jsonify(_helpers.submit())
