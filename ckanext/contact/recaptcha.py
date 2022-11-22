import requests
from ckan.plugins import toolkit


class RecaptchaError(ValueError):
    pass


def check_recaptcha(token, expected_action):
    """
    Check a user's recaptcha token is valid, and raise RecaptchaError if it's not. If
    the token is valid then this function has no side effects.

    :param token: the token as returned in the frontend by a call to execute
    :param expected_action: the expected action associated with the token
    """
    key = toolkit.config.get('ckanext.contact.recaptcha_v3_key', False)
    secret = toolkit.config.get('ckanext.contact.recaptcha_v3_secret', False)

    if not key or not secret:
        # recaptcha not enabled
        return

    post_params = {
        'secret': secret,
        'response': token,
    }
    client_ip_address = toolkit.request.environ.get('REMOTE_ADDR', None)
    if client_ip_address:
        post_params['remoteip'] = client_ip_address

    response = requests.post(
        'https://www.google.com/recaptcha/api/siteverify', params=post_params
    )
    response.raise_for_status()
    result = response.json()

    if not result['success']:
        raise RecaptchaError(', '.join(result['error-codes']))
    if expected_action != result['action']:
        raise RecaptchaError(toolkit._('Action mismatch'))
