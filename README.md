<!--header-start-->
<img src="https://data.nhm.ac.uk/images/nhm_logo.svg" align="left" width="150px" height="100px" hspace="40"/>

# ckanext-contact

[![Tests](https://img.shields.io/github/actions/workflow/status/NaturalHistoryMuseum/ckanext-contact/main.yml?style=flat-square)](https://github.com/NaturalHistoryMuseum/ckanext-contact/actions/workflows/main.yml)
[![Coveralls](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-contact/main?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-contact)
[![CKAN](https://img.shields.io/badge/ckan-2.9.7-orange.svg?style=flat-square)](https://github.com/ckan/ckan)
[![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg?style=flat-square)](https://www.python.org/)
[![Docs](https://img.shields.io/readthedocs/ckanext-contact?style=flat-square)](https://ckanext-contact.readthedocs.io)

_A CKAN extension for adding popup contact forms to pages._

<!--header-end-->

# Overview

<!--overview-start-->
Borrows much of the contact form code from [ckanext-surrey](https://github.com/CityofSurrey/ckanext-surrey).

An example can be seen on the Natural History Museum's [Data Portal](https://data.nhm.ac.uk) when clicking "_Contact dataset curator._"

This extension now includes Google's [reCAPTCHA](https://www.google.com/recaptcha) for preventing spam submissions.

<!--overview-end-->

# Installation

<!--installation-start-->
Path variables used below:
- `$INSTALL_FOLDER` (i.e. where CKAN is installed), e.g. `/usr/lib/ckan/default`
- `$CONFIG_FILE`, e.g. `/etc/ckan/default/development.ini`

## Installing from PyPI

```shell
pip install ckanext-contact
```

## Installing from source

1. Clone the repository into the `src` folder:
   ```shell
   cd $INSTALL_FOLDER/src
   git clone https://github.com/NaturalHistoryMuseum/ckanext-contact.git
   ```

2. Activate the virtual env:
   ```shell
   . $INSTALL_FOLDER/bin/activate
   ```

3. Install via pip:
   ```shell
   pip install $INSTALL_FOLDER/src/ckanext-contact
   ```

### Installing in editable mode

Installing from a `pyproject.toml` in editable mode (i.e. `pip install -e`) requires `setuptools>=64`; however, CKAN 2.9 requires `setuptools==44.1.0`. See [our CKAN fork](https://github.com/NaturalHistoryMuseum/ckan) for a version of v2.9 that uses an updated setuptools if this functionality is something you need.

## Post-install setup

1. Add 'contact' to the list of plugins in your `$CONFIG_FILE`:
   ```ini
   ckan.plugins = ... contact
   ```

2. To use reCAPTCHA, you must register a site with the Google [reCAPTCHA](https://www.google.com/recaptcha) service and add your API key and secret in the [configuration](#configuration).

<!--installation-end-->

# Configuration

<!--configuration-start-->
These are the options that can be specified in your .ini config file.

## Email

| Name                                       | Description                                       | Default                         |
|--------------------------------------------|---------------------------------------------------|---------------------------------|
| `ckanext.contact.mail_to`                  | Email address to submit to                        | `email_to`                      |
| `ckanext.contact.recipient_name`           | Name of the recipient                             | `ckan.site_title`               |
| `ckanext.contact.subject`                  | Email subject for the submitted form              | 'Contact/Question from visitor' |
| `ckanext.contact.add_timestamp_to_subject` | Whether to append a timestamp to the subject line | `false`                         |
| `ckanext.contact.subject_prefix`           | A prefix to add to the subject before sending     | ''                              |

## Recaptcha

| Name                                  | Description                              | Default               |
|---------------------------------------|------------------------------------------|-----------------------|
| `ckanext.contact.recaptcha_v3_key`    | API key for the reCAPTCHA service.       | False (i.e. disabled) |
| `ckanext.contact.recaptcha_v3_secret` | API secret for the reCAPTCHA service.    | False (i.e. disabled) |
| `ckanext.contact.recaptcha_v3_action` | `data-module-action` for the form/button |                       |

## Other

| Name                          | Description                                                                                          | Default             |
|-------------------------------|------------------------------------------------------------------------------------------------------|---------------------|
| `ckanext.contact.check_email` | Set to False to disable checking email addresses via [pyIsEmail](https://pypi.org/project/pyIsEmail) | True (i.e. enabled) |

<!--configuration-end-->

# Usage

<!--usage-start-->
Add the following HTML where you want the contact button to appear:

```html+jinja
{% set params = {...} %}

<a class="btn btn-primary" data-module="modal-contact" data-module-template="{{ h.get_contact_form_template_url(params) }}" href="{{ h.url_for('contact.form', **params) }}" title="{{ _('Contact') }}">
    <i class="fas fa-envelope"></i>{{ link_text if link_text else _('CONTACT BUTTON TEXT') }}
</a>

{% asset 'ckanext-contact/main' %}
```

Where `params` is a dict with three entries: package_id, resource_id, record_id (all of which are optional).

<!--usage-end-->

# Testing

<!--testing-start-->
There is a Docker compose configuration available in this repository to make it easier to run tests. The ckan image uses the Dockerfile in the `docker/` folder.

To run the tests against ckan 2.9.x on Python3:

1. Build the required images:
   ```shell
   docker-compose build
   ```

2. Then run the tests.
   The root of the repository is mounted into the ckan container as a volume by the Docker compose
   configuration, so you should only need to rebuild the ckan image if you change the extension's
   dependencies.
   ```shell
   docker-compose run ckan
   ```

<!--testing-end-->
