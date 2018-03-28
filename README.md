# CKAN Contact Extension

[![Travis branch](https://img.shields.io/travis/NaturalHistoryMuseum/ckanext-contact/master.svg?style=flat-square)](https://travis-ci.org/NaturalHistoryMuseum/ckanext-contact) [![Coveralls github branch](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-contact/master.svg?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-contact)

This extension adds a contact form

**DEMO:** http://data.nhm.ac.uk/

**Settings**

     ckanext.contact.mail_to =
     ckanext.contact.recipient_name =
     ckanext.contact.subject =

If ckanext.contact.mail_to is not set, the form will fall back to using the CKAN setting "email_to".

**Credits:**

Borrows much of the contact form code from https://github.com/CityofSurrey/ckanext-surrey
