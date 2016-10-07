Monzo Python
============

A basic Python (2.7) wrapper for the Monzo API

Monzo API docs: https://monzo.com/docs/

Monzo API playground: https://developers.monzo.com/api/playground


Installation
------------

Clone this repo then:

``pip install -e .``


Running the tests
-----------------
.. code:: python

    pip install tox
    export MONZO_CLIENT_SECRET={client_secret}
    export MONZO_CLIENT_ID={client_id}

    tox


Or if you want to run and debug tests:

``py.test -sv --cov monzo``



Example Usage
-------------

**Basic Usage**

*Note - All methods simply return the json from each request. This is only a thin wrapper around the API*

.. code:: python

    monzo = MonzoClient(CLIENT_ID, CLIENT_SECRET, 'http://localhost:5000')
    monzo.get_authorization_code()
    token_info = monzo.get_access_token(code)
    monzo.update_tokens(**tokens)

    monzo.whoami()
    monzo.list_accounts()
    monzo.get_balance(account_id=None)
    monzo.list_transactions(account_id=None, limit=100, since='', before='')  # NOQA
    monzo.get_transaction(transactions_id)
    monzo.annotate_transaction(transactions_id, metadata)
    monzo.remove_annotations(transactions_id, annotation_keys)
    monzo.get_feed(account_id=None)
    monzo.create_feed_item()
    monzo.list_webhooks(account_id=None)
    monzo.create_webhook(webhook_url, account_id=None)
    monzo.remove_webhook(webhook_id, account_id=None)
    monzo.upload_attachment(file_path)
    monzo.attach_file(transaction_id, file_url, file_type)
    monzo.remove_attachment(attachment_id)

**Tip** - ``update_tokens`` takes the response from either get_access_token or refresh_access_token and sets everything up ready for the API calls. It also gets the first account_id so you don't need to keep passing them around (hence why a large number of the methods have ``account_id=None``)


**Flask**
This repo includes a [basic flask example](example/flask/app.py)


ToDo
----
-  Perhaps split client into multiple files
-  Raise correct errors
-  Python 3+ support


Bugs
----
-  .
