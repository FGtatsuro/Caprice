#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from .config import settings

def create_app(global_config, **local_conf):
    return _create_app(settings[local_conf['config_key']])

def _create_app(setting):
    app = Flask(__name__)

    app.config.from_object(setting)
    if app.debug:
        DebugToolbarExtension(app)

    from .views import main
    app.register_blueprint(main)
    return app
