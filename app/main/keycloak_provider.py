from app.main import auth_bp as bp
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
from flask import current_app

import os

@bp.route('/keycloak_login')
def keycloak_login():
    idp = get_idp()
    nonce = generate_token()
    redirect_uri = url_for('auth.keycloak_authorize', _external=True, nonce=nonce)
    print("Redirect URI: " + redirect_uri)
    return idp.authorize_redirect(redirect_uri, nonce=nonce)

@bp.route('/login/oauth2/code/keycloak')
def keycloak_authorize(nonce=None):
    idp = get_idp()
    token = idp.authorize_access_token()
    user_info = idp.parse_id_token(token, nonce=nonce)
    session['profile'] = user_info
    return redirect("/")

def get_idp():
    idp=None
    if current_app.OAUTH.create_client('KEYCLOAK'):
        idp = current_app.OAUTH.KEYCLOAK
    else:
        idp = current_app.OAUTH.register(
            name="KEYCLOAK",
            client_secret=os.getenv('KEYCLOAK_CLIENT_SECRET'),
            client_kwargs={"scope": "openid profile email"},
            server_metadata_url=f'https://{current_app.config["KEYCLOAK_DOMAIN"]}/.well-known/openid-configuration'
        )
    return idp