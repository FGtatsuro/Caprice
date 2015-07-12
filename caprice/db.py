#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

__all__ = ['init', 'Session', 'Base']

# TODO: Access privilege(user/password) for database
# TODO: DB URL should be set from config
engine = create_engine('postgresql://localhost/caprice')
Session = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
Base = declarative_base()
Base.query = Session.query_property()

def init(app):
    # TODO: logger
    print('Init database')
    from . import models
    Base.metadata.create_all(bind=engine)

    @app.teardown_appcontext
    def shutdown(exception):
        # TODO: logger
        print('Clear session.')
        Session.remove()
