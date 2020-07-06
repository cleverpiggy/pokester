from os import environ
from functools import wraps
import json
from flask import session, redirect, render_template, url_for
from dotenv import load_dotenv, find_dotenv
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

AUTH0_CALLBACK_URL = environ.get('AUTH0_CALLBACK_URL')
AUTH0_CLIENT_ID = environ.get('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = environ.get('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = environ.get('AUTH0_DOMAIN')
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = environ.get('AUTH0_AUDIENCE')


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            # Redirect to Login page here
            return redirect('/')
        return f(*args, **kwargs)

    return decorated


def setup_auth(app):

    oauth = OAuth(app)

    auth0 = oauth.register(
        'auth0',
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        api_base_url=AUTH0_BASE_URL,
        access_token_url=AUTH0_BASE_URL + '/oauth/token',
        authorize_url=AUTH0_BASE_URL + '/authorize',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )

    @app.route('/callback')
    def callback_handling():
        # Handles response from token endpoint
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        # Store the user information in flask session.
        session['jwt_payload'] = userinfo
        session['profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }
        return redirect('/games')

    @app.route('/login', methods=['POST', 'GET'])
    def login():
        # https://auth0.com/docs/universal-login/default-login-url?_ga=2.99410717.2004209071.1594001273-1129603475.1594001273
        # The login_url should point to a route in the application that ends up
        # redirecting to Auth0's /authorize endpoint, e.g. https://mycompany.org/login.
        # Note that it requires https and it cannot point to localhost.
        return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL)

    @app.route('/dashboard')
    @requires_auth
    def dashboard():
        return render_template('dashboard.html',
                               userinfo=session['profile'],
                               userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))

    @app.route('/logout')
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        params = {'returnTo': url_for('index', _external=True), 'client_id': AUTH0_CLIENT_ID}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

    #     # https://auth0.com/docs/logout?_ga=2.96988828.2004209071.1594001273-1129603475.1594001273
    #     # 1. clear the session cookies
    #     # 2. log out with auth0 api
    #     # https://YOUR_DOMAIN/v2/logout
    #     return 'logged out!'
