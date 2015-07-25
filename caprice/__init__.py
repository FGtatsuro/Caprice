#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from logging import DEBUG

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from .config import settings
from .db import init as init_db

def create_app(global_config, **local_conf):
    # TODO: Use PasteDeploy config directly.
    conf = settings[local_conf['config_key']]
    conf.DATABASE_URL = local_conf['database_url']
    return _create_app(conf)
    #return _create_app(settings[local_conf['config_key']])

def _create_app(setting):
    app = Flask(__name__)

    app.logger.setLevel(DEBUG)
    app.logger.debug('Init root logger.')

    app.config.from_object(setting)
    if app.debug:
        DebugToolbarExtension(app)

    from .views import api
    app.register_blueprint(api, url_prefix='/api')

    init_db(app)

    return app
