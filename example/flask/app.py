# -*- coding: utf-8 -*-

import os

from flask import Flask, redirect, url_for, make_response, request, jsonify
from itsdangerous import URLSafeSerializer

from monzo import MonzoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'changeme'

SIGNER = URLSafeSerializer('secret-key')
CLIENT_ID = os.getenv('MONZO_CLIENT_ID')
CLIENT_SECRET = os.getenv('MONZO_CLIENT_SECRET')

monzo = MonzoClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    login_url='http://localhost:5000/login/'
)


@app.route('/')
def home():
    if request.cookies.get('tokens'):
        tokens = SIGNER.loads(request.cookies.get('tokens'))
        monzo.update_tokens(**tokens)
        ctx = {'whoami': monzo.whoami()}
    else:
        ctx = {'Login': 'Please go to /login/ to login'}
    return jsonify(**ctx)


@app.route('/login/')
def login():
    if not request.args.get('code'):
        return redirect(monzo.get_authorization_code())
    else:
        code = request.args.get('code')
        cookie = monzo.get_access_token(code)
        resp = make_response(redirect(url_for('home')))
        resp.set_cookie('tokens', SIGNER.dumps(cookie))
        return resp


if __name__ == '__main__':
    app.run()
