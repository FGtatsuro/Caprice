#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, String

from .db import Base, Session

__all__ = ['Schema']

class Schema(Base):

    __tablename__ = 'schemas'

    # TODO: allow Only UUID? or user defined ID too?
    id = Column(String, primary_key=True)
    # TODO: JSON uniqueness is needed
    body = Column(String)

    # ID is generated in Python context(=in application)
    def __init__(self, id=None, body=None):
        self.id = id
        self.body = body

    def __repr__(self):
        return "<{0}: '{1}'>".format(self.__class__.__name__, self.body)

    # TODO: Use contextmanager. Ref. http://docs.sqlalchemy.org/en/rel_1_0/orm/session_basics.html
    def save(self):
        s = Session()
        s.add(self)
        try:
            # TODO: logger
            s.commit()
        except:
            s.rollback()
            # TODO: Error message
            raise RuntimeError('')
        finally:
            # TODO: logger
            s.close()
