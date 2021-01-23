# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-contact
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit


@toolkit.auth_allow_anonymous_access
def send_contact(context, data_dict):
    '''

    :param context:
    :param data_dict:

    '''
    if True:
        return {
            'success': True
        }
    else:
        return {
            'success': False,
            'msg': 'Not allowed to use contact form'
        }
