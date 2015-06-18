#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from paste.deploy import loadapp

_app = loadapp(
    'config:config.ini', 
    name=os.environ.get('ENVIRONMENT_TYPE', 'develop'), 
    relative_to='.')

if __name__ == '__main__':
    _app.run(
        host='127.0.0.1',
        port=int(os.environ.get('PORT', 5000)))