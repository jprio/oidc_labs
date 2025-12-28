from flask import Flask, redirect, url_for, session, render_template, jsonify
from authlib.integrations.flask_client import OAuth
import json
from werkzeug.middleware.proxy_fix import ProxyFix

oauth = OAuth()
def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('app.config')
    app.secret_key = 'your_secret_key'
    app.debug = True
    app.development = True
    # Initialize Flask extensions here

    # Register blueprints here
    from app.main import auth_bp
    app.register_blueprint(auth_bp) 

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

    oauth.init_app(app)
    app.OAUTH=oauth

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'

    @app.route('/logout')
    def logout():
        print("Logging out user...")
        session.clear()
        return redirect('/')

    @app.route('/')
    def hello_world():
        user_info=None
        if session.get("profile"):
            # json.load(session.get("profile"))
            user_info = session.get("profile")
            print(type(user_info))
            print("User info found in session: " + json.dumps(user_info, indent=4)  )
        if user_info:
            return render_template('user.html', user_info=json.dumps(user_info, indent=4))
        return '<a href="/github_login">Login with Github</a><br><a href="/auth0_login">Login with auth0</a><br><a href="/keycloak_login">Login with keycloak</a>'

    return app