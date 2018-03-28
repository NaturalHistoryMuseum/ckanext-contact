#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-contact
# Created by the Natural History Museum in London, UK

from logging import getLogger

from ckanext.contact.auth import send_contact

from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit

log = getLogger(__name__)


class ContactPlugin(SingletonPlugin):
    '''CKAN Contact Extension'''
    implements(interfaces.IRoutes, inherit=True)
    implements(interfaces.IConfigurer)
    implements(interfaces.IAuthFunctions)

    ## IConfigurer
    def update_config(self, config):
        '''

        :param config: 

        '''
        toolkit.add_template_directory(config, u'theme/templates')
        toolkit.add_public_directory(config, u'theme/public')
        toolkit.add_resource(u'theme/public', u'ckanext-contact')

    ## IRoutes
    def before_map(self, map):
        '''

        :param map: 

        '''

        # Add controller for KE EMu specimen records
        map.connect(u'contact_form', '/contact',
                    controller=u'ckanext.contact.controllers.contact:ContactController',
                    action=u'form')

        # Add AJAX request handler
        map.connect(u'contact_ajax_submit', '/contact/ajax',
                    controller=u'ckanext.contact.controllers.contact:ContactController',
                    action=u'ajax_submit')

        return map

    ## IAuthFunctions
    def get_auth_functions(self):
        ''' '''
        return {
            u'send_contact': send_contact
            }
