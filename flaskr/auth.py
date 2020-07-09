from os import environ
from functools import wraps
import json
from flask import session, redirect, render_template, url_for, jsonify, request
from dotenv import load_dotenv, find_dotenv
# from authlib.integrations.flask_client import OAuth

# @TODO see if I can just use from urllib import urlencode, url open
# to avoid the six dependancy
from six.moves.urllib.parse import urlencode
from six.moves.urllib.request import urlopen
from jose import jwt

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = environ.get('AUTH0_CALLBACK_URL')
AUTH0_CLIENT_ID = environ.get('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = environ.get('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = environ.get('AUTH0_DOMAIN')
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = environ.get('AUTH0_AUDIENCE')

ALGORITHMS = ["RS256"]


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Format error response and append status code
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token



def verify_decode_jwt():
    token = get_token_auth_header()
    jsonurl = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception:
        raise AuthError({
            "code": "invalid_header",
            "description": "Authorization malformed."
        }, 401)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if not rsa_key:
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=AUTH0_AUDIENCE,
            issuer="https://" + AUTH0_DOMAIN + "/"
        )
    except jwt.ExpiredSignatureError:
        raise AuthError({"code": "token_expired",
                        "description": "token is expired"}, 401)
    except jwt.JWTClaimsError:
        raise AuthError({"code": "invalid_claims",
                        "description":
                            "incorrect claims,"
                            "please check the audience and issuer"}, 401)
    except Exception:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Unable to parse authentication"
                            " token."}, 401)
    return payload


def check_permissions(permission, payload):
    if not permission:
        return True
    permissions = payload.get('permissions')
    if permissions is None:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
            }, status_code=401)
    if permission not in permissions:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permission not found.'
            }, status_code=401)
    return True


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            payload = verify_decode_jwt()
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator


# used for testing functionality ignoring authorization
def requires_auth_dummy(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f({}, *args, **kwargs)
        return wrapper
    return requires_auth_decorator


# @TODO I don't think I'll need setup_auth now, these are just routes
def setup_auth(app):


    # @TODO state is about mitigating a CSRF attack by attaching some random info,
    # store it on the client side (sessions), and AUTH0 will return the same string to check against
    # https://en.wikipedia.org/wiki/Cross-site_request_forgery
    # scope needs to be appended to authorize_url for /userinfo to work
    authorize_url = f"https://{AUTH0_DOMAIN}/authorize?audience={AUTH0_AUDIENCE}&response_type=token&client_id={AUTH0_CLIENT_ID}&redirect_uri={AUTH0_CALLBACK_URL}&scope=openid%20profile%20email"


    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    @app.route('/callback')
    def callback():
        # Handles response from token endpoint

        # @TODO maybe implement this so we can get user info

        # It looks like we can't get the token this way
        # We would have to request 'code' then get the token later.

        # token = something_about_get_token()
        # method = 'GET'
        # url = f"https://{AUTH0_DOMAIN}/userinfo"
        # header = f"Authorization: 'Bearer {token}"

        # Store the user information in flask session.
        # session['jwt_payload'] = userinfo
        # session['profile'] = {
        #     'user_id': userinfo['sub'],
        #     'name': userinfo['name'],
        #     'picture': userinfo['picture']
        # }
        return redirect('/home')

    @app.route('/login', methods=['POST', 'GET'])
    def login():
        # https://auth0.com/docs/universal-login/default-login-url?_ga=2.99410717.2004209071.1594001273-1129603475.1594001273
        # The login_url should point to a route in the application that ends up
        # redirecting to Auth0's /authorize endpoint, e.g. https://mycompany.org/login.
        # Note that it requires https and it cannot point to localhost.
        return redirect(authorize_url)


    @app.route('/logout')
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        params = {'returnTo': url_for('index', _external=True), 'client_id': AUTH0_CLIENT_ID}
        return redirect(AUTH0_BASE_URL + '/v2/logout?' + urlencode(params))

    #     # 1. clear the session cookies
    #     # 2. log out with auth0 api
    #     # https://YOUR_DOMAIN/v2/logout
    #     return 'logged out!'
