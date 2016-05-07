import os
import urllib
import requests
from urlparse import urljoin
from mimetypes import MimeTypes
from datetime import datetime, timedelta


class MondoClient(object):

    def __init__(
        self,
        client_id,
        client_secret,
        login_url,
        access_token=None,
        refresh_token=None,
        account_id=None,
    ):
        self.token_url = 'https://api.getmondo.co.uk/oauth2/token'
        self.api_url = 'https://api.getmondo.co.uk/'
        self.auth_url = 'https://auth.getmondo.co.uk/'
        self.client_id = client_id
        self.client_secret = client_secret
        self.login_url = login_url
        self.access_token = access_token if access_token else ''
        self.refresh_token = refresh_token if refresh_token else ''
        self.account_id = account_id if account_id else ''
        self.expires_at = '3000-12-31T23:59:59.999999'

    def get(self, url):
        return self.request(url=url, method='GET')

    def post(self, url, data):
        return self.request(url=url, method='POST', data=data)

    def patch(self, url, data):
        return self.request(url=url, method='PATCH', data=data)

    def delete(self, url):
        return self.request(url=url, method='DELETE')

    def request(self, **kwargs):
        self._ensure_access_token()

        if kwargs['url'].endswith('/'):
            kwargs['url'] = kwargs['url'][:-1]

        if 'method' in kwargs:
            kwargs['method'] = kwargs['method'].upper()
        else:
            kwargs['method'] = 'GET'

        kwargs['headers'] = {'Authorization': 'Bearer {0}'.format(self.access_token)}  # NOQA
        if 'data' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/x-www-form-urlencoded'  # NOQA

        response = requests.request(**kwargs)
        response.raise_for_status()
        return response.json()

    def get_authorization_code(self):
        query = urllib.urlencode({
            'client_id': self.client_id,
            'redirect_uri': self.login_url,
            'response_type': 'code',
        })
        url = urljoin(self.auth_url, '?{0}'.format(query))
        return url

    def get_access_token(self, code):
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.login_url,
            'code': code,
        }
        response = self.post(url=self.token_url, data=data)
        self.access_token = response['access_token']
        self.refresh_token = response['refresh_token']
        response['expires_at'] = self._set_expires_at(response['expires_in'])
        return response

    def refresh_access_token(self, refresh_token=None):
        if refresh_token:
            self.refresh_token = refresh_token
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
        }

        response = self.post(url=self.token_url, data=data)
        self.access_token = response['access_token']
        self.refresh_token = response['refresh_token']
        response['expires_at'] = self._set_expires_at(response['expires_in'])
        return response

    def _set_expires_at(self, expires_in):
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        self.expires_at = expires_at.isoformat()
        return self.expires_at

    def _ensure_access_token(self):
        expires_at = datetime.strptime(self.expires_at, "%Y-%m-%dT%H:%M:%S.%f")
        if datetime.now() > expires_at:
            self.refresh_access_token()

    def update_tokens(self, **kwargs):
        self.access_token = kwargs['access_token']
        self.refresh_token = kwargs['refresh_token']
        self.expires_at = kwargs['expires_at']
        if 'account_id' in kwargs:
            self.account_id = kwargs['account_id']
        else:
            accounts = self.list_accounts()
            self.account_id = accounts['accounts'][0]['id']
        self._ensure_access_token()
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.expires_at,
            'account_id': self.account_id,
        }

    def whoami(self):
        url = urljoin(self.api_url, 'ping/whoami')
        response = self.get(url)
        return response

    def list_accounts(self):
        url = urljoin(self.api_url, 'accounts')
        response = self.get(url)
        return response

    def get_balance(self, account_id=None):
        if account_id:
            self.account_id = account_id

        url = urljoin(self.api_url, 'balance?account_id={0}'.format(self.account_id))  # NOQA
        response = self.get(url)
        return response

    def list_transactions(self, account_id=None, limit=100, since='', before=''):  # NOQA
        if account_id:
            self.account_id = account_id

        query = {
            'account_id': self.account_id,
            'expand[]': 'merchant',
            'limit': limit,
            'since': since,
            'before': before,
        }

        query = urllib.urlencode(query)
        url = urljoin(self.api_url, 'transactions?{0}'.format(query))
        response = self.get(url)
        return response['transactions']

    def get_transaction(self, transactions_id):
        url = urljoin(
            self.api_url,
            'transactions/{0}?expand[]=merchant'.format(transactions_id)
        )
        response = self.get(url)
        return response['transaction']

    def annotate_transaction(self, transactions_id, metadata):
        """ Metadata is just a key:value pair """

        url = urljoin(self.api_url, 'transactions/{0}'.format(transactions_id))
        data = {}
        for key, value in metadata.items():
            data['metadata[{}]'.format(key)] = value

        response = self.patch(url, data=data)
        return response['transaction']

    def remove_annotations(self, transactions_id, annotation_keys):
        """ annotation_keys is a list of keys to remove """

        url = urljoin(self.api_url, 'transactions/{0}'.format(transactions_id))
        data = {}
        for key in annotation_keys:
            data['metadata[{}]'.format(key)] = ''

        response = self.patch(url, data=data)
        return response

    def get_feed(self, account_id=None):
        if account_id:
            self.account_id = account_id

        url = urljoin(self.api_url, 'feed?account_id={0}'.format(self.account_id))  # NOQA
        response = self.get(url)
        return response

    def create_feed_item(
        self, title, image_url, url=None, body=None,
        background_color=None, title_color=None, body_color=None,
        account_id=None
    ):
        if account_id:
            self.account_id = account_id

        url = urljoin(self.api_url, 'feed')
        data = {
            'account_id': self.account_id,
            'type': 'basic',
            'params[title]': title,
            'params[image_url]': image_url
        }
        if url:
            data['url'] = url
        if body:
            data['params[body]'] = body
        if background_color:
            data['params[background_color]'] = background_color
        if title_color:
            data['params[title_color'] = title_color
        if body_color:
            data['params[body_color'] = body_color

        response = self.post(url, data=data)
        return response

    def list_webhooks(self, account_id=None):
        if account_id:
            self.account_id = account_id

        url = urljoin(self.api_url, 'webhooks?account_id={0}'.format(self.account_id))  # NOQA
        response = self.get(url)
        return response['webhooks']

    def create_webhook(self, webhook_url, account_id=None):
        if account_id:
            self.account_id = account_id
        url = urljoin(self.api_url, 'webhooks')
        data = {
            'account_id': self.account_id,
            'url': webhook_url,
        }
        response = self.post(url, data)
        return response['webhook']

    def remove_webhook(self, webhook_id, account_id=None):
        if account_id:
            self.account_id = account_id

        url = urljoin(self.api_url, 'webhooks/{0}'.format(webhook_id))
        response = self.delete(url)
        return response

    def upload_attachment(self, file_path):
        __, file_name = os.path.split(file_path)
        mime = MimeTypes()
        url = urllib.pathname2url(file_path)
        mime_type, __ = mime.guess_type(url)

        data = {
            'file_name': file_name,
            'file_type': mime_type
        }
        url = urljoin(self.api_url, 'attachment/upload')
        response = self.post(url, data=data)

        with open(file_path) as fh:
            file_data = fh.read()

        upload_response = requests.put(
            response['upload_url'],
            data=file_data,
            headers={'content-type': mime_type},
            params={'file': file_path}
        )
        upload_response.raise_for_status()

        return {
            'file_url': response['file_url'],
            'file_type': mime_type,
        }

    def attach_file(self, transaction_id, file_url, file_type):
        url = urljoin(self.api_url, 'attachment/register')
        data = {
            'external_id': transaction_id,
            'file_url': file_url,
            'file_type': file_type
        }
        response = self.post(url, data=data)
        return response['attachment']

    def remove_attachment(self, attachment_id):
        url = urljoin(self.api_url, 'attachment/deregister')
        data = {'id': attachment_id}
        response = self.post(url, data=data)
        return response
