#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-contact
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

version = u'0.2'

setup(
    name=u'ckanext-contact',
    version=version,
    description=u'CKAN Extension providing Contact / Feedback form',
    classifiers=[],
    keywords=u'',
    author=u'Ben Scott',
    author_email=u'ben@benscott.co.uk',
    url=u'',
    license=u'',
    packages=find_packages(exclude=[u'tests']),
    namespace_packages=[u'ckanext', u'ckanext.contact'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points= \
        u'''
        [ckan.plugins]
            contact=ckanext.contact.plugin:ContactPlugin
        ''',
    )
