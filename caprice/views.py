#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import uuid
from logging import getLogger

from flask import Blueprint, Response
from flask import jsonify, render_template, redirect, url_for, request
from jsonschema import Draft4Validator, SchemaError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from .db import Session
from .models import *

# Handlers of this logger depends on Flask application
logger = getLogger(__name__)

api = Blueprint('api', __name__)

@api.route('/schemas', methods=['GET', 'POST'])
def schema():
    # TODO: controller is needed?
    if request.method == 'GET':
        # TODO: JSON-Model mapping
        # TODO: Pagination
        res = jsonify({'schemas': [{'id': s.id, 'body': s.json} for s in Schema.query.all()]})
        return res
    if request.method == 'POST':
        body = request.get_json(silent=True)
        # TODO: Sophisticated error handling
        if not body:
            res = jsonify({'error': {'message': 'Request is invalid.'}})
            res.status_code = 400
            return res
        try:
            _id = str(uuid.uuid4())
            schema = Schema(id=_id, json=body)
            schema.save()
            Session.commit()
            Session.refresh(schema)
            # TODO: JSON-Model mapping
            res = jsonify({'id': _id})
            res.status_code = 201
        except Exception as e:
            Session.rollback()
            # TODO: Error handler
            logger.error(str(e))
            res = jsonify({'error': {'message': str(e)}})
            res.status_code = 400
        return res

@api.route('/schemas/<string:_id>', methods=['GET', 'PUT', 'DELETE'])
def schema_id(_id):
    # TODO: DRY. controller is needed?
    if request.method == 'PUT':
        body = request.get_json(silent=True)
        if not body:
            res = jsonify({'error': {'message': 'Request is invalid.'}})
            res.status_code = 400
            return res
        try:
            schema = Schema(id=_id, json=body)
            schema.save()
            Session.commit()
            Session.refresh(schema)
            res = jsonify({'id': _id})
            res.status_code = 201
            return res
        # TODO: Error handler
        except IntegrityError as e:
            Session.rollback()
            logger.error(str(e))
            res = jsonify({'error': {'message': 'This schema ID is already used.'}})
            res.status_code = 409
            return res
        except Exception as e:
            Session.rollback()
            logger.error(str(e))
            res = jsonify({'error': {'message': str(e)}})
            res.status_code = 400
            return res

    schema = Schema.query.filter(Schema.id==_id).first()
    if not schema:
        res = jsonify({'error': {'message': "Schema isn't found."}})
        res.status_code = 404
        return res
    # TODO: Error handling
    if request.method == 'GET':
        res = jsonify(schema.json)
        res.status_code = 200
        return res
    if request.method == 'DELETE':
        schema.delete()
        Session.commit()
        res = Response('')
        res.status_code = 204
        return res

@api.route('/schemas/<string:schema_id>/resources', methods=['GET', 'POST'])
def resource(schema_id):
    # TODO: DRY. Same process exists in schema API
    schema = Schema.query.filter(Schema.id==schema_id).first()
    if not schema:
        res = jsonify({'error': {'message': "Schema isn't found."}})
        res.status_code = 404
        return res
    # TODO: controller is needed?
    if request.method == 'GET':
        # TODO: JSON-Model mapping
        # TODO: Pagination
        resources = Resource.query.filter(Resource.schema_id==schema_id).all()
        res = jsonify({'resources': [{'id': r.id, 'body': r.json} for r in resources]})
        return res
    if request.method == 'POST':
        # TODO: DRY. Same process exists in schema API
        body = request.get_json(silent=True)
        if not body:
            res = jsonify({'error': {'message': 'Request is invalid.'}})
            res.status_code = 400
            return res
        try:
            resource_id = str(uuid.uuid4())
            resource = Resource(resource_id, body, schema)
            resource.save()
            Session.commit()
            Session.refresh(resource)
            # TODO: JSON-Model mapping
            res = jsonify({'id': resource_id})
            res.status_code = 201
            return res
        except Exception as e:
            Session.rollback()
            # TODO: Error handler
            logger.error(str(e))
            res = jsonify({'error': {'message': str(e)}})
            res.status_code = 400
            return res

# TODO: How to present parent relations of REST resources?
@api.route('/schemas/<string:schema_id>/resources/<string:resource_id>', methods=['GET', 'PUT', 'DELETE'])
def resource_id(schema_id, resource_id):
    # TODO: DRY. Same process exists in schema API
    schema = Schema.query.filter(Schema.id==schema_id).first()
    if not schema:
        res = jsonify({'error': {'message': "Schema isn't found."}})
        res.status_code = 404
        return res

    # TODO: DRY. controller is needed?
    if request.method == 'PUT':
        body = request.get_json(silent=True)
        if not body:
            res = jsonify({'error': {'message': 'Request is invalid.'}})
            res.status_code = 400
            return res
        try:
            resource = Resource(resource_id, body, schema)
            resource.save()
            Session.commit()
            Session.refresh(resource)
            # TODO: JSON-Model mapping
            res = jsonify({'id': resource_id})
            res.status_code = 201
            return res
        # TODO: Error handler
        except FlushError as e:
            Session.rollback()
            logger.error(str(e))
            res = jsonify({'error': {'message': 'This resource ID is already used.'}})
            res.status_code = 409
            return res
        except Exception as e:
            Session.rollback()
            logger.error(str(e))
            res = jsonify({'error': {'message': str(e)}})
            res.status_code = 400
            return res

    resource = Resource.query.filter(Resource.id==resource_id).first()
    if not resource:
        res = jsonify({'error': {'message': "Resource isn't found."}})
        res.status_code = 404
        return res
    # TODO: Error handling
    if request.method == 'GET':
        res = jsonify(resource.json)
        res.status_code = 200
        return res
    if request.method == 'DELETE':
        resource.delete()
        Session.commit()
        res = Response('')
        res.status_code = 204
        return res

@api.route('/locks', methods=['GET', 'POST'])
def lock():
    if request.method == 'POST':
        body = request.get_json(silent=True)
        if not body and body['resources']:
            res = jsonify({'error': {'message': 'Request is invalid.'}})
            res.status_code = 400
            return res
        resources = Resource.query.filter(Resource.id.in_(body['resources'])).all()
        for r_id in body['resources']:
            if not (r_id in [resource.id for resource in resources]):
                res = jsonify({'error': {'message': "Resource {0} isn't found.".format(r_id)}})
                res.status_code = 404
                return res
        # TODO: Move this logic to Service layer
        try:
            lock = Lock(resources)
            lock.save()
            Session.commit()
            Session.refresh(lock)
            # TODO: JSON-Model mapping
            res = jsonify({'id': lock.id})
            res.status_code = 201
            return res
        except Exception as e:
            Session.rollback()
            # TODO: Error handler
            logger.error(str(e))
            res = jsonify({'error': {'message': str(e)}})
            res.status_code = 400
            return res

@api.route('/locks/<int:_id>', methods=['GET', 'DELETE'])
def lock_id(_id):
    res = Response('')
    res.data = str(_id)
    if request.method == 'DELETE':
        res.status_code = 204
    return res
