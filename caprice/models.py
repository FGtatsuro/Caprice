#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from jsonschema import Draft4Validator, SchemaError
from sqlalchemy import Column, String

from .db import Base, Session

__all__ = ['Schema']

class Schema(Base):

    __tablename__ = 'schemas'

    # TODO: allow Only UUID? or user defined ID too?
    id = Column(String, primary_key=True)
    # TODO: JSON uniqueness is needed
    # This value represents raw JSON string. 
    # If you want to get JSON object(=dictionary), please use json property.
    body = Column(String)

    # ID is generated in Python context(=in application)
    def __init__(self, id=None, json=None):
        self.id = id
        self.json = json
        self._validate()

    @property
    def json(self):
        # TODO: logger
        return json.loads(self.body)

    @json.setter
    def json(self, value):
        # TODO: logger
        self.body = json.dumps(value)

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

    def _validate(self):
        # Draft4Validator accepts empty JSON, but we don't want to accept it.
        if not self.json:
            raise ValueError('Schema is invalid.')
        try:
            Draft4Validator.check_schema(self.json)
        except SchemaError as e:
            raise ValueError('Schema is invalid.')
