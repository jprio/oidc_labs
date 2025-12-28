from flask import Blueprint
from flask import current_app
auth_bp = Blueprint('auth', __name__)
from app.main import github_provider
from app.main import auth0_provider
from app.main import keycloak_provider