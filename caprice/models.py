#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from logging import getLogger

from jsonschema import Draft4Validator, SchemaError, ValidationError, validate
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from .db import Base, Session

# Handlers of this logger depends on Flask application
logger = getLogger(__name__)

__all__ = ['Schema', 'Resource']

class Schema(Base):

    __tablename__ = 'schemas'

    # TODO: allow Only UUID? or user defined ID too?
    id = Column(String, primary_key=True)
    # TODO: JSON uniqueness is needed
    # This value represents raw JSON string. 
    # If you want to get JSON object(=dictionary), please use json property.
    body = Column(String)

    # ID is generated in Python context(=in application)
    def __init__(self, id, json):
        self.id = id
        self.json = json
        self._validate()

    @property
    def json(self):
        return json.loads(self.body)

    @json.setter
    def json(self, value):
        self.body = json.dumps(value)

    def __repr__(self):
        return "<{0}: '{1}'>".format(self.__class__.__name__, self.body)

    # TODO: Use contextmanager. Ref. http://docs.sqlalchemy.org/en/rel_1_0/orm/session_basics.html
    def save(self):
        s = Session()
        s.add(self)
        try:
            logger.debug('Commit: {0}'.format(self))
            s.commit()
        except Exception as e:
            logger.error('Rollback: {0}. Error details: {1}'.format(self, e))
            s.rollback()
            # TODO: Sophisticated error handling
            raise ValueError('This schema ID is already used.')
        finally:
            logger.debug('Close: {0}'.format(self.__class__.__name__))
            s.close()

    def delete(self):
        s = Session()
        s.delete(self)
        try:
            logger.debug('Commit: {0}'.format(self))
            s.commit()
        except Exception as e:
            logger.error('Rollback: {0}. Error details: {1}'.format(self, e))
            s.rollback()
            # TODO: Sophisticated error handling
            raise ValueError('Deleting schema is failed.')
        finally:
            logger.debug('Close: {0}'.format(self.__class__.__name__))
            s.close()

    def _validate(self):
        # Draft4Validator accepts empty JSON, but we don't want to accept it.
        if not self.json:
            raise ValueError('Schema is invalid.')
        try:
            Draft4Validator.check_schema(self.json)
        except (SchemaError, ValidationError):
            raise ValueError('Schema is invalid.')

# TODO: Schema hierarchy (Ref. http://docs.sqlalchemy.org/en/rel_1_0/orm/inheritance.html)
class Resource(Base):

    __tablename__ = 'resources'

    # TODO: allow Only UUID? or user defined ID too?
    id = Column(String, primary_key=True)
    # TODO: JSON uniqueness is needed
    # This value represents raw JSON string. 
    # If you want to get JSON object(=dictionary), please use json property.
    body = Column(String)

    schema_id = Column(String, ForeignKey('schemas.id'))
    schema = relationship('Schema', backref=backref('resources', order_by='Resource.id'))

    # ID is generated in Python context(=in application)
    def __init__(self, id, json, schema):
        self.id = id
        self.json = json
        self.schema_id = schema.id
        self.schema = schema
        self._validate()

    @property
    def json(self):
        return json.loads(self.body)

    @json.setter
    def json(self, value):
        self.body = json.dumps(value)

    def __repr__(self):
        return "<{0}: '{1}'>".format(self.__class__.__name__, self.body)

     # TODO: Use contextmanager. Ref. http://docs.sqlalchemy.org/en/rel_1_0/orm/session_basics.html
    def save(self):
        s = Session()
        s.add(self)
        try:
            logger.debug('Commit: {0}'.format(self))
            s.commit()
        except Exception as e:
            logger.error('Rollback: {0}. Error details: {1}'.format(self, e))
            s.rollback()
            # TODO: Sophisticated error handling
            raise ValueError('This resource ID is already used.')
        finally:
            logger.debug('Close: {0}'.format(self.__class__.__name__))
            s.close()

    def delete(self):
        s = Session()
        s.delete(self)
        try:
            logger.debug('Commit: {0}'.format(self))
            s.commit()
        except Exception as e:
            logger.error('Rollback: {0}. Error details: {1}'.format(self, e))
            s.rollback()
            # TODO: Sophisticated error handling
            raise ValueError('Deleting resource is failed.')
        finally:
            logger.debug('Close: {0}'.format(self.__class__.__name__))
            s.close()

    def _validate(self):
        # Draft4Validator accepts empty JSON, but we don't want to accept it.
        if not self.json:
            raise ValueError('Resource is invalid.')
        try:
            validate(self.json, self.schema.json)
        except (SchemaError, ValidationError):
            raise ValueError('Resource is invalid.')
