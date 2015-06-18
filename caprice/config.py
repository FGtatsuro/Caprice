#!/usr/bin/env python
# -*- coding: utf-8 -*-

class DevelopConfig(object):
    DEBUG = True
    SECRET_KEY = 'debug_secretkey'

class ProductionConfig(object):
    import os
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

settings = {
    'develop': DevelopConfig,
    'production': ProductionConfig,
}
