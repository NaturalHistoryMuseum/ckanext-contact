"""
CKAN Contact Extension
"""
import os
from logging import getLogger
import ckan.plugins as p
from ckanext.contact.auth import send_contact

log = getLogger(__name__)

class ContactPlugin(p.SingletonPlugin):
    """
    CKAN Contact Extension
    """
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer)
    p.implements(p.IAuthFunctions)

    ## IConfigurer
    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/public', 'ckanext-contact')

    ## IRoutes
    def before_map(self, map):

        # Add controller for KE EMu specimen records
        map.connect('contact_form', '/contact',
                    controller='ckanext.contact.controllers.contact:ContactController',
                    action='form')

        # Add AJAX request handler
        map.connect('contact_ajax_submit', '/contact/ajax',
                    controller='ckanext.contact.controllers.contact:ContactController',
                    action='ajax_submit')

        return map

    ## IAuthFunctions
    def get_auth_functions(self):
        return {'send_contact': send_contact}

