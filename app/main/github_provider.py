from app.main import auth_bp as bp
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
from flask import current_app

import os

@bp.route('/github_login')
def github_login():
    idp = get_idp()
    nonce = generate_token()
    redirect_uri = url_for('auth.github_authorize', _external=True, nonce=nonce)
    print("Redirect URI: " + redirect_uri)
    return idp.authorize_redirect(redirect_uri, nonce=nonce)

@bp.route('/login/oauth2/code/github')
def github_authorize(nonce=None):
    idp = get_idp()
    token = idp.authorize_access_token()
    session['token'] = token
    resp = idp.get('user', token=token)
    profile = resp.json()
    user_info = idp.parse_id_token(token, nonce=nonce)
    session['profile'] = profile
    # print("user_info : " + str(user_info))
    return redirect("/")

def get_idp():
    idp=None
    if current_app.OAUTH.create_client('GITHUB'):
        idp = current_app.OAUTH.GITHUB
    else:
        idp = current_app.OAUTH.register(
            name='GITHUB'
            , client_secret=os.getenv('_GITHUB_CLIENT_SECRET')
            , client_kwargs={'scope': 'openid profile email'}
        )
    return idp