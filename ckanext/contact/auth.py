#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import os
import ckan.plugins as p

@p.toolkit.auth_allow_anonymous_access
def send_contact(context, data_dict):
    if True:
        return {'success': True}
    else:
        return {'success': False, 'msg': 'Not allowed to use contact form'}