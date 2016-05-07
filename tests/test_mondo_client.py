import os
import json

import pytest

TEST_WEBHOOK_URL = 'http://example.com/mondotestwebhooks'


@pytest.yield_fixture()
def webhook(client):
    webhook = client.create_webhook(webhook_url=TEST_WEBHOOK_URL)
    yield webhook
    client.remove_webhook(webhook_id=webhook['id'])


@pytest.yield_fixture()
def add_annotation(client):
    annotation_key = 'testannotation'
    transactions = client.list_transactions()
    transaction_id = transactions[0]['id']
    metadata = {annotation_key: annotation_key}
    client.annotate_transaction(transaction_id, metadata)
    yield {
        'transaction_id': transaction_id,
        'annotation_key': annotation_key
    }
    client.remove_annotations(transaction_id, [annotation_key])


@pytest.yield_fixture()
def add_attachment(client):
    transactions = client.list_transactions()
    transaction_id = transactions[0]['id']
    base_dir = os.path.dirname(__file__)
    file_path = '{0}/mondo-logo.png'.format(base_dir)
    file_upload = client.upload_attachment(file_path)
    attachment = client.attach_file(
        transaction_id,
        file_upload['file_url'],
        file_upload['file_type']
    )
    yield {
        'attachment_id': attachment['id'],
        'transaction_id': transaction_id
    }
    client.remove_attachment(attachment['id'])


class TestMondoClient:

    def test_refresh_access_token(self, client):
        access_token = client.access_token
        refresh_token = client.refresh_token
        token_info = client.refresh_access_token()

        base_dir = os.path.dirname(__file__)
        token_file = '{0}/token_info.json'.format(base_dir)
        with open(token_file, 'w') as fp:
            json.dump(token_info, fp)

        assert access_token != client.access_token
        assert refresh_token != client.refresh_token

    def test_update_tokens(self, client):
        client.access_token = None
        client.refresh_token = None
        client.expires_at = None
        client.account_id = None
        base_dir = os.path.dirname(__file__)
        with open(os.path.join(base_dir, 'token_info.json')) as data_file:
            tokens = json.load(data_file)
        client.update_tokens(**tokens)

        assert client.access_token
        assert client.refresh_token
        assert client.expires_at
        assert client.account_id

    def test_whoami(self, client):
        whoami = client.whoami()
        assert whoami
        assert 'user_id' in whoami
        assert 'authenticated' in whoami
        assert 'client_id' in whoami

    def test_list_accounts(self, client):
        accounts = client.list_accounts()
        assert len(accounts) > 0

    def test_get_balance(self, client):
        balance = client.get_balance()
        assert 'currency' in balance
        assert 'balance' in balance
        assert 'spend_today' in balance

    def test_list_transactions(self, client):
        transactions = client.list_transactions()
        assert len(transactions) > 0

    def test_get_transaction(self, client):
        transactions = client.list_transactions()
        transaction_id = transactions[0]['id']
        transaction = client.get_transaction(transaction_id)
        assert transaction['id'] == transactions[0]['id']

    def test_annotate_transaction(self, client):
        annotation_key = 'testannotation'
        transactions = client.list_transactions()
        transaction_id = transactions[0]['id']
        metadata = {annotation_key: annotation_key}
        transaction = client.annotate_transaction(transaction_id, metadata)
        assert 'testannotation' in transaction['metadata']

        client.remove_annotations(transaction_id, [annotation_key])

    def test_remove_annotations(self, client, add_annotation):
        transaction_id = add_annotation['transaction_id']
        annotation_key = add_annotation['annotation_key']
        client.remove_annotations(transaction_id, [annotation_key])
        transaction = client.get_transaction(transaction_id)
        assert annotation_key not in transaction['metadata']

    def test_create_feed_item(self, client):
        feed_item_name = 'mondo-python test_create_feed_item'
        image_url = 'https://raw.githubusercontent.com/pyepye/mondo-python/master/tests/mondo-logo.png'  # NOQA
        feed_created = client.create_feed_item(feed_item_name, image_url)
        assert type(feed_created) is dict
        feed = client.get_feed()
        found_feed_item = False
        for item in feed['items']:
            if item['params']['title'] == feed_item_name:
                found_feed_item = True
                break
        assert found_feed_item

    def test_list_webhooks(self, client, webhook):
        webhooks = client.list_webhooks()
        assert len(webhooks) > 0

    def test_create_webhook(self, client):
        webhook = client.create_webhook(webhook_url=TEST_WEBHOOK_URL)
        assert webhook['url'] == TEST_WEBHOOK_URL
        assert webhook['account_id'] == client.account_id

        webhook = client.remove_webhook(webhook_id=webhook['id'])

    def test_delete_webhook(self, client, webhook):
        webhook = client.create_webhook(webhook_url=TEST_WEBHOOK_URL)
        current_webhooks = client.list_webhooks()
        number_of_hooks = len(current_webhooks)
        client.remove_webhook(webhook_id=webhook['id'])
        webhooks = client.list_webhooks()
        assert len(webhooks) < number_of_hooks

    def test_add_attachment(self, client):
        transactions = client.list_transactions()
        transaction_id = transactions[0]['id']

        base_dir = os.path.dirname(__file__)
        file_path = '{0}/mondo-logo.png'.format(base_dir)
        file_upload = client.upload_attachment(file_path)
        assert file_upload['file_type'] == 'image/png'
        assert 'file_url' in file_upload

        attachment = client.attach_file(
            transaction_id,
            file_upload['file_url'],
            file_upload['file_type']
        )
        assert 'id' in attachment
        assert attachment['file_type'] == file_upload['file_type']
        assert attachment['file_url'] == file_upload['file_url']
        assert attachment['external_id'] == transaction_id
        client.remove_attachment(attachment['id'])

    def test_remove_attachment(self, client, add_attachment):
        transaction_id = add_attachment['transaction_id']
        attachment_id = add_attachment['attachment_id']

        transaction = client.get_transaction(transaction_id)
        number_of_attachments = transaction['attachments']
        client.remove_attachment(attachment_id)
        transaction = client.get_transaction(transaction_id)
        assert transaction['attachments'] < number_of_attachments
