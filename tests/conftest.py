import os
import sys
import json
import subprocess
import webbrowser
from datetime import datetime
from urlparse import urlparse, parse_qs


import pytest

from mondo import MondoClient


@pytest.fixture(scope="module")
def client():
    client_secret = os.getenv('MONDO_CLIENT_SECRET')
    if not client_secret:
        raise ValueError('MONDO_CLIENT_SECRET environment variable must be set')  # NOQA
    client_id = os.getenv('MONDO_CLIENT_ID')
    if not client_id:
        raise ValueError('MONDO_CLIENT_ID environment variable must be set')

    try:
        base_url = os.path.dirname(__file__)
        with open(os.path.join(base_url, 'token_info.json')) as data_file:
            tokens = json.load(data_file)
    except IOError:
        tokens = setup_access(client_id, client_secret)

    expires_at = datetime.strptime(tokens['expires_at'], "%Y-%m-%dT%H:%M:%S.%f")  # NOQA
    if datetime.now() > expires_at:
        tokens = setup_access(client_id, client_secret)

    login_url = 'http://example.com/login/'
    mondo = MondoClient(
        client_id=client_id,
        client_secret=client_secret,
        login_url=login_url,
        access_token=tokens['access_token'],
        refresh_token=tokens['refresh_token'],
    )
    mondo.update_tokens(**tokens)
    return mondo


def setup_access(client_id, client_secret):

    mondo = MondoClient(client_id, client_secret, 'http://example.com/login/')
    auth_url = mondo.get_authorization_code()

    print '\nA browser will now open, please login and copy the URL once authenticated'  # NOQA
    if sys.platform == 'darwin':
        subprocess.Popen(['open', auth_url])
    else:
        webbrowser.open_new_tab(auth_url)

    url = raw_input("\nPlease enter the url from the 'Log in to Mondo' button in the authentication email: ")  # NOQA
    url = urlparse(url)
    query = parse_qs(url.query)
    code = query['code'][0]
    token_info = mondo.get_access_token(code)

    base_dir = os.path.dirname(__file__)
    token_file = '{0}/token_info.json'.format(base_dir)
    with open(token_file, 'w') as fp:
        json.dump(token_info, fp)

    print 'Token info exported to: {0}'.format(token_file)
    return token_info
