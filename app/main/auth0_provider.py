from app.main import auth_bp as bp
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
from flask import current_app

import os

@bp.route('/auth0_login')
def auth0_login():
    idp = get_idp()
    nonce = generate_token()
    redirect_uri = url_for('auth.auth0_authorize', _external=True, nonce=nonce)
    return idp.authorize_redirect(redirect_uri, nonce=nonce)

@bp.route('/login/oauth2/code/auth0')
def auth0_authorize(nonce=None):
    idp = get_idp()
    token = idp.authorize_access_token()
    user_info = idp.parse_id_token(token, nonce=nonce)
    session['profile'] = user_info
    return redirect("/")

def get_idp():
    idp=None
    if current_app.OAUTH.create_client('AUTH0'):
        idp = current_app.OAUTH.AUTH0
    else:
        idp = current_app.OAUTH.register(
            name='AUTH0'
            , client_kwargs={'scope': 'openid profile email'}
            , client_secret=os.getenv('AUTH0_CLIENT_SECRET')
            , server_metadata_url=f'https://{current_app.config["AUTH0_DOMAIN"]}/.well-known/openid-configuration'
        )
    return idp