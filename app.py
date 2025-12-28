from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix

import os
app = Flask(__name__)
app.config.from_pyfile('app.config')

oauth = OAuth(app)
github=oauth.register(
    name='GITHUB'
    ,    client_kwargs={'scope': 'user:email'}
)

auth0=oauth.register(
    name='AUTH0'
    ,    client_kwargs={'scope': 'openid profile email'}
    ,    server_metadata_url=f'https://{app.config["AUTH0_DOMAIN"]}/.well-known/openid-configuration'

)

keycloak = oauth.register(
    name="KEYCLOAK",
    client_id="account",
    client_secret="1691MG30Fwp8XCX12mk5GHuM1C6S9dwt",
    server_metadata_url="https://keycloak.staging.e-auth.cloud/realms/jprio_realm1/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"},
)
app.secret_key = 'your_secret_key'
app.config['SESSION_COOKIE_NAME'] = 'flask_oidc_session'
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

@app.route('/')
def hello_world():
    user_info = session.get('profile')
    if user_info:
        return f'Hello, {user_info} !     <a href="/logout">Logout</a>'
    return '<a href="/github_login">Login with Github</a><br><a href="/auth0_login">Login with auth0</a><br><a href="/keycloak_login">Login with keycloak</a>'

@app.route('/github_login')
def github_login():
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)

@app.route('/keycloak_login')
def keycloak_login():
    redirect_uri = url_for('keycloak_authorize', _external=True)
    return keycloak.authorize_redirect(redirect_uri)

@app.route('/auth0_login')
def auth0_login():
    redirect_uri = url_for('auth0_authorize', _external=True)
    print(redirect_uri)
    return auth0.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
 
@app.route('/github')
def show_github_profile():
    resp = github.get('user', token=session.get('token'))
    resp.raise_for_status()
    profile = resp.json()
    return profile

@app.route('/login/oauth2/code/github')
def github_authorize():
    token = github.authorize_access_token()
    print(token)
    session['token'] = token
    resp = github.get('user', token=token)
    profile = resp.json()
    session['profile'] = profile
    return redirect("/")

@app.route('/login/oauth2/code/auth0')
def auth0_authorize():
    token = auth0.authorize_access_token()
    print(token)
    session['profile'] = token
    return redirect("/")

@app.route('/login/oauth2/code/keycloak')
def keycloak_authorize():
    token = keycloak.authorize_access_token()
    print(token)
    session['profile'] = token
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
