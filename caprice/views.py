#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import uuid
from logging import getLogger

from flask import Blueprint, Response
from flask import jsonify, render_template, redirect, url_for, request
from jsonschema import Draft4Validator, SchemaError

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
            # TODO: JSON-Model mapping
            res = jsonify({'id': _id})
            res.status_code = 201
        except ValueError as e:
            res = jsonify({'error': {'message': str(e)}})
            res.status_code = 400
        return res

@api.route('/schemas/<string:_id>', methods=['GET', 'PUT', 'DELETE'])
def schema_id(_id):
    if request.method == 'GET':
        res = Response('')
        res.data = _id
        res.status_code = 200
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
            res = jsonify({'id': _id})
            res.status_code = 201
        except ValueError as e:
            res = jsonify({'error': {'message': str(e)}})
            res.status_code = 400
    if request.method == 'DELETE':
        res = Response('')
        res.status_code = 204
    return res

@api.route('/resources', methods=['GET', 'POST'])
def resource():
    res = Response('')
    if request.method == 'POST':
        res.status_code = 201
    return res

@api.route('/resources/<int:_id>', methods=['GET', 'PUT', 'DELETE'])
def resource_id(_id):
    res = Response('')
    res.data = str(_id)
    if request.method == 'DELETE':
        res.status_code = 204
    return res

@api.route('/locks', methods=['GET', 'POST'])
def lock():
    res = Response('')
    if request.method == 'POST':
        res.status_code = 201
    return res

@api.route('/locks/<int:_id>', methods=['GET', 'DELETE'])
def lock_id(_id):
    res = Response('')
    res.data = str(_id)
    if request.method == 'DELETE':
        res.status_code = 204
    return res
