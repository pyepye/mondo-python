import os
import json
import subprocess
import webbrowser
import sys
from urlparse import urlparse, parse_qs
from pprint import pprint

from mondo.mondo import MondoClient


def setup_access():
    if not os.environ.get('MONDO_CLIENT_SECRET'):
        CLIENT_SECRET = raw_input("Please enter your client secret: ")
        if not CLIENT_SECRET:
            raise ValueError('MONDO_CLIENT_SECRET environment variable must be set')  # NOQA
    if not os.environ.get('MONDO_CLIENT_ID'):
        CLIENT_ID = raw_input("Please enter your client ID: ")
        if not CLIENT_ID:
            raise ValueError('MONDO_CLIENT_ID environment variable must be set')  # NOQA

    mondo = MondoClient(CLIENT_ID, CLIENT_SECRET, 'http://testurl/login/')
    auth_url = mondo.get_authorization_code()

    print 'A browser will now open, please login and copy the URL once authenticated'  # NOQA
    if sys.platform == 'darwin':
        subprocess.Popen(['open', auth_url])
    else:
        webbrowser.open_new_tab(auth_url)

    url = raw_input("Please enter the full URL that you got redirected to: ")
    url = urlparse(url)
    query = parse_qs(url.query)
    code = query['code'][0]
    token_info = mondo.get_access_token(code)
    print '\n Token info: '
    pprint(token_info)

    base_dir = os.path.dirname(__file__)
    token_file = '{0}/../tests/token_info.json'.format(base_dir)
    with open(token_file, 'w') as fp:
        json.dump(token_info, fp)
    print 'Token info exported to: {0}'.format(token_file)


if __name__ == '__main__':
    setup_access()
