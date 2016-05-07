Mondo Python
=============

Python wrapper for the Mondo API

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
    python tools/setup_access.py

    tox


Or if you want to run and debug tests:

``py.test -sv --cov mondo``



Example Usage
-------------
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
-  Finish writing tests
-  Raise correct errors
-  Python 3+ support


Bugs
----
-  .
