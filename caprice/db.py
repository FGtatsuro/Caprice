#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

__all__ = ['init', 'Session', 'Base']

# Handlers of this logger depends on Flask application
logger = getLogger(__name__)

# TODO: Access privilege(user/password) for database
# TODO: DB URL should be set from config
Session = scoped_session(sessionmaker(autoflush=False, autocommit=False))
Base = declarative_base()

def init(app):
    engine = create_engine(app.config['DATABASE_URL'])
    Session.configure(bind=engine)
    Base.query = Session.query_property()

    logger.debug('Init database')
    from . import models
    Base.metadata.create_all(bind=engine)

    @app.teardown_appcontext
    def shutdown(exception):
        logger.debug('Clear session.')
        Session.remove()
