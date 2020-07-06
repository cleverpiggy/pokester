"""Hi"""
import os

def Config(app=None):
    """Return a configuration dictionary.
    Use either the app configuration or the os environment.
    """
    if app:
        config = app.config
    else:
        config = os.environ
    return config
