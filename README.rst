Mondo Python
=============

A basic Python (2.7) wrapper for the Mondo API

Mondon API docs: https://getmondo.co.uk/docs/

Mondon API playground: https://developers.getmondo.co.uk/api/playground


Installation
------------

Clone this repo then:

``pip install -e .``


Running the tests
-----------------
.. code:: python

    pip install tox
    export MONDO_CLIENT_SECRET={client_secret}
    export MONDO_CLIENT_ID={client_id}

    tox


Or if you want to run and debug tests:

``py.test -sv --cov mondo``



Example Usage
-------------

**Basic Usage**

*Note - All methods simply return the json from each request. This is only a thin wrapper around the API*

.. code:: python

    mondo = MondoClient(CLIENT_ID, CLIENT_SECRET, 'http://localhost:5000')
    mondo.get_authorization_code()
    token_info = mondo.get_access_token(code)
    mondo.update_tokens(**tokens)

    mondo.whoami()
    mondo.list_accounts()
    mondo.get_balance(account_id=None)
    mondo.list_transactions(account_id=None, limit=100, since='', before='')  # NOQA
    mondo.get_transaction(transactions_id)
    mondo.annotate_transaction(transactions_id, metadata)
    mondo.remove_annotations(transactions_id, annotation_keys)
    mondo.get_feed(account_id=None)
    mondo.create_feed_item()
    mondo.list_webhooks(account_id=None)
    mondo.create_webhook(webhook_url, account_id=None)
    mondo.remove_webhook(webhook_id, account_id=None)
    mondo.upload_attachment(file_path)
    mondo.attach_file(transaction_id, file_url, file_type)
    mondo.remove_attachment(attachment_id)

**Tip** - ``update_tokens`` takes the response from either get_access_token or refresh_access_token and sets everything up ready for the API calls. It also gets the first account_id so you don't need to keep passing them around (hence why a large number of the methods have ``account_id=None``)


**Flask**

.. code:: python

    mondo = MondoClient(CLIENT_ID, CLIENT_SECRET, 'http://localhost:5000')
    ...
    @app.route('/')
    def home():
        if request.cookies.get('tokens'):
            tokens = SIGNER.loads(request.cookies.get('tokens'))
            mondo.update_tokens(**tokens)
            ctx = {'whoami': mondo.whoami()}
        else:
            ctx = {'noauth': True}
        return render_template('index.html', **ctx)

    @app.route('/login/')
    def login():
        if not request.args.get('code'):
            return redirect(mondo.get_authorization_code())
        else:
            code = request.args.get('code')
            cookie = mondo.get_access_token(code)
            resp = make_response(redirect(url_for('home')))
            resp.set_cookie('tokens', SIGNER.dumps(cookie))
            return resp
    ...


ToDo
----
-  Perhaps split client into multiple files
-  Raise correct errors
-  Python 3+ support


Bugs
----
-  .
