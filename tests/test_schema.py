#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import json

import pytest

from caprice import _create_app
from caprice.models import Schema
from caprice.db import Session

@pytest.fixture
def client(request):
    class TestConfig(object):
        TESTING = True
        DATABASE_URL = 'sqlite:///caprice_test.db'
    app = _create_app(TestConfig)
    client = app.test_client()

    # CleanUp
    # TODO: should use mock for DB?
    Session()
    Session.query(Schema).delete()
    Session.commit()
    Session.remove()
    return client

def test_schema_registration(client):

    # 'application/json'
    res = client.post(
            '/api/schemas', 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/json'})
    assert res.status_code == 201
    assert uuid.UUID(json.loads(res.data.decode('utf-8'))['id'])    
    # 'application/xxxx+json'
    res = client.post(
            '/api/schemas', 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 201
    assert uuid.UUID(json.loads(res.data.decode('utf-8'))['id'])    

def test_schema_registration_with_id(client):
    _id = 'testid'
    res = client.put(
            '/api/schemas/{0}'.format(_id), 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/json'})
    assert res.status_code == 201
    assert json.loads(res.data.decode('utf-8'))['id'] == _id
    res = client.put(
            '/api/schemas/{0}'.format(_id), 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/json'})
    assert res.status_code == 409
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'This schema ID is already used.'}})

def test_schema_registration_invalid_header(client):

    # No header
    res = client.post(
            '/api/schemas', 
            data=json.dumps({'aaa':1}))
    assert res.status_code == 400 
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})
    # not 'application/xxx+json'
    res = client.post(
            '/api/schemas', 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'text/plain'})
    assert res.status_code == 400 
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})

def test_schema_registration_invalid_data(client):

    # Violation of JSON Schema Draft4
    res = client.post(
            '/api/schemas', 
            data=json.dumps({"type": "obj"}), 
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Schema is invalid.'}})
    # No date
    res = client.post(
            '/api/schemas',
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})
    # Empty date. None/str/json
    res = client.post(
            '/api/schemas', 
            data=None,
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})
    res = client.post(
            '/api/schemas', 
            data='',
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})
    res = client.post(
            '/api/schemas',
            data=json.dumps({}),
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})

def test_schema_registration_with_id_invalid_data(client):

    # Violation of JSON Schema Draft4
    res = client.put(
            '/api/schemas/violatejsonschema', 
            data=json.dumps({"type": "obj"}), 
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Schema is invalid.'}})
    # No date
    res = client.put(
            '/api/schemas/nodata',
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})
    # Empty date. None/str/json
    res = client.put(
            '/api/schemas/nonedata', 
            data=None,
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})
    res = client.put(
            '/api/schemas/emptystr', 
            data='',
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})
    res = client.put(
            '/api/schemas/emptyjson',
            data=json.dumps({}),
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})

def test_schema_list(client):
    res = client.get('/api/schemas', follow_redirects=True)
    assert res.status_code == 200
    assert len(json.loads(res.data.decode('utf-8'))['schemas']) == 0

    schema = {'aaa':1}
    client.post(
            '/api/schemas', 
            data=json.dumps(schema), 
            headers={'content-type':'application/caprise+json'})

    res = client.get('/api/schemas', follow_redirects=True)
    assert res.status_code == 200
    schemas = json.loads(res.data.decode('utf-8'))['schemas']
    assert len(schemas) == 1
    # TODO: JSONSchema validation
    assert schemas[0]['id']
    assert schemas[0]['body'] == schema

    schema = {'bbb':1}
    client.post(
            '/api/schemas', 
            data=json.dumps(schema), 
            headers={'content-type':'application/caprise+json'})
    res = client.get('/api/schemas', follow_redirects=True)
    assert res.status_code == 200
    schemas = json.loads(res.data.decode('utf-8'))['schemas']
    assert len(schemas) == 2

def test_schema_get(client):
    schema = {'aaa':1}
    res = client.post(
            '/api/schemas', 
            data=json.dumps(schema), 
            headers={'content-type':'application/caprise+json'})
    res = client.get(
            '/api/schemas/{0}'.format(json.loads(res.data.decode('utf-8'))['id']))
    assert res.status_code == 200
    assert json.loads(res.data.decode('utf-8')) == schema

    schema = {'aaa':2}
    _id = 'testget'
    res = client.put(
            '/api/schemas/{0}'.format(_id), 
            data=json.dumps(schema), 
            headers={'content-type':'application/caprise+json'})
    res = client.get(
            '/api/schemas/{0}'.format(json.loads(res.data.decode('utf-8'))['id']))
    assert res.status_code == 200
    assert json.loads(res.data.decode('utf-8')) == schema

def test_schema_delete(client):
    _id = 'notfoundschema'
    res = client.delete('/api/schemas/{0}'.format(_id))
    assert res.status_code == 404
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': "Schema isn't found."}})

    _id = 'foundschema'
    res = client.put(
            '/api/schemas/{0}'.format(_id), 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/caprise+json'})
    res = client.delete('/api/schemas/{0}'.format(_id))
    assert res.status_code == 204
    res = client.get('/api/schemas/{0}'.format(_id))
    assert res.status_code == 404
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': "Schema isn't found."}})
