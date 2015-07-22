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
    s = Session()
    s.query(Schema).delete()
    s.commit()
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
    assert json.loads(schemas[0]['body']) == schema

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
    res = client.get('/api/schemas/1', follow_redirects=True)
    assert res.status_code == 200
    assert res.data == b'1'
    res = client.delete('/api/schemas/1', follow_redirects=True)
    assert res.status_code == 204
    res = client.put('/api/schemas/1', follow_redirects=True)
    assert res.status_code == 405

def test_resource(client):
    res = client.get('/api/resources', follow_redirects=True)
    assert res.status_code == 200
    res = client.post('/api/resources', follow_redirects=True)
    assert res.status_code == 201

    res = client.get('/api/resources/1', follow_redirects=True)
    assert res.status_code == 200
    assert res.data == b'1'
    res = client.delete('/api/resources/1', follow_redirects=True)
    assert res.status_code == 204
    res = client.put('/api/resources/1', follow_redirects=True)
    assert res.status_code == 200

def test_lock(client):
    res = client.get('/api/locks', follow_redirects=True)
    assert res.status_code == 200
    res = client.post('/api/locks', follow_redirects=True)
    assert res.status_code == 201

    res = client.get('/api/locks/1', follow_redirects=True)
    assert res.status_code == 200
    assert res.data == b'1'
    res = client.delete('/api/locks/1', follow_redirects=True)
    assert res.status_code == 204
    res = client.put('/api/locks/1', follow_redirects=True)
    assert res.status_code == 405
