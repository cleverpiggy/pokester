import os
from flask import Flask
from flask_cors import CORS
from .models import setup_db
from .controllers import register_views
from .auth import setup_auth

def create_app(test_config=None):
    app = Flask(__name__)

    # @TODO work out this config crap wrt heroku environ etc.
    if test_config:
        app.config.from_object(test_config)

    dbpath = os.environ.get('DATABASE_URL')
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    setup_db(app, dbpath)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        return response

    register_views(app)
    setup_auth(app)

    return app
