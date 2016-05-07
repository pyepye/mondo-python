import os
import json
from datetime import datetime
from mondo import MondoClient

import pytest


@pytest.fixture
def client():
    CLIENT_SECRET = os.getenv('MONDO_CLIENT_SECRET')
    # print "{0}".format(CLIENT_SECRET)
    if not CLIENT_SECRET:
        raise ValueError('MONDO_CLIENT_SECRET environment variable must be set')  # NOQA
    CLIENT_ID = os.getenv('MONDO_CLIENT_ID')
    if not CLIENT_ID:
        raise ValueError('MONDO_CLIENT_ID environment variable must be set')  # NOQA

    try:
        base_url = os.path.dirname(__file__)
        with open(os.path.join(base_url, 'token_info.json')) as data_file:
            tokens = json.load(data_file)
    except IOError:
        raise IOError('Please run - python -m tools/setup_access.py')

    expires_at = datetime.strptime(tokens['expires_at'], "%Y-%m-%dT%H:%M:%S.%f")  # NOQA
    if datetime.now() > expires_at:
        raise ValueError('Please re-run - python -m tools/setup_access.py')

    login_url = 'http://example.com/login/'
    mondo = MondoClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        login_url=login_url,
        access_token=tokens['access_token'],
        refresh_token=tokens['refresh_token'],
    )
    mondo.update_tokens(**tokens)
    return mondo
