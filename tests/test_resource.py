#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import json

import pytest

from caprice import _create_app
from caprice.models import Schema, Resource
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
    s.query(Resource).delete()
    s.commit()
    return client

def test_resource_registration(client):
    res = client.post(
            '/api/schemas', 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/json'})
    schema_id = json.loads(res.data.decode('utf-8'))['id']

    # 'application/json'
    res = client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/json'})
    assert res.status_code == 201
    resource_id = str(uuid.UUID(json.loads(res.data.decode('utf-8'))['id']))
    resource = Resource.query.filter(Resource.id==resource_id).first()
    assert resource
    assert resource.id == resource_id

    # 'application/xxxx+json'
    res = client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 201
    resource_id = str(uuid.UUID(json.loads(res.data.decode('utf-8'))['id']))
    resource = Resource.query.filter(Resource.id==resource_id).first()
    assert resource
    assert resource.id == resource_id

def test_resource_registration_notfound_schema(client):
    schema_id = 'notfoundschema'
    res = client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/json'})
    assert res.status_code == 404 
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': "Schema isn't found."}})

def test_resource_registration_invalid_header(client):
    res = client.post(
            '/api/schemas', 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/json'})
    schema_id = json.loads(res.data.decode('utf-8'))['id']

    # No header
    res = client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=json.dumps({'aaa':1}))
    assert res.status_code == 400 
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})
    # not 'application/xxx+json'
    res = client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'text/plain'})
    assert res.status_code == 400 
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})

def test_resource_registration_invalid_data(client):
    res = client.post(
            '/api/schemas', 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/json'})
    schema_id = json.loads(res.data.decode('utf-8'))['id']

    # No date
    res = client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})
    # Empty date. None/str/json
    res = client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=None,
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})
    res = client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data='',
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})
    res = client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=json.dumps({}),
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Request is invalid.'}})

    # Violation of parent schema
    schema = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'title': 'testschema',
        'description': 'for test',
        'type': 'object',
        'properties': {
            'hoge': {
                'type': 'string'
            }
        },
        'required': [
            'hoge'
        ]
    }
    res = client.post(
            '/api/schemas', 
            data=json.dumps(schema), 
            headers={'content-type':'application/json'})
    schema_id = json.loads(res.data.decode('utf-8'))['id']
    res = client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/caprise+json'})
    assert res.status_code == 400
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'Resource is invalid.'}})

def test_resource_registration_with_id(client):
    res = client.post(
            '/api/schemas', 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/json'})
    schema_id = json.loads(res.data.decode('utf-8'))['id']

    resource_id = 'testid'
    res = client.put(
            '/api/schemas/{0}/resources/{1}'.format(schema_id, resource_id), 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/json'})
    assert res.status_code == 201
    assert json.loads(res.data.decode('utf-8'))['id'] == resource_id
    resource = Resource.query.filter(Resource.id==resource_id).first()
    assert resource
    assert resource.id == resource_id

    res = client.put(
            '/api/schemas/{0}/resources/{1}'.format(schema_id, resource_id), 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/json'})
    assert res.status_code == 400 
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': 'This resource ID is already used.'}})

def test_resource_list(client):
    schema = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'title': 'testschema',
        'description': 'for test',
        'type': 'object',
        'properties': {
            'hoge': {
                'type': 'string'
            }
        },
        'required': [
            'field1'
        ]
    }
    res = client.post(
            '/api/schemas', 
            data=json.dumps(schema), 
            headers={'content-type':'application/json'})
    schema_id = json.loads(res.data.decode('utf-8'))['id']

    res = client.get('/api/schemas/{0}/resources'.format(schema_id))
    assert res.status_code == 200
    assert len(json.loads(res.data.decode('utf-8'))['resources']) == 0

    resource = {'field1': 1}
    client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=json.dumps(resource), 
            headers={'content-type':'application/caprise+json'})

    res = client.get('/api/schemas/{0}/resources'.format(schema_id))
    assert res.status_code == 200
    resources = json.loads(res.data.decode('utf-8'))['resources']
    assert len(resources) == 1
    # TODO: JSONSchema validation
    assert resources[0]['id']
    assert resources[0]['body'] == resource

    resource = {'field1': 2}
    client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=json.dumps(resource), 
            headers={'content-type':'application/caprise+json'})
    # Failed request 
    resource = {'bbb':1}
    client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=json.dumps(resource), 
            headers={'content-type':'application/caprise+json'})

    res = client.get('/api/schemas/{0}/resources'.format(schema_id))
    assert res.status_code == 200
    resources = json.loads(res.data.decode('utf-8'))['resources']
    assert len(resources) == 2

    # Another schema doesn't affect list result
    res = client.post(
            '/api/schemas', 
            data=json.dumps({'a': 1}), 
            headers={'content-type':'application/json'})
    another_schema_id = json.loads(res.data.decode('utf-8'))['id']
    client.post(
            '/api/schemas/{0}/resources'.format(another_schema_id), 
            data=json.dumps({'a': 1}), 
            headers={'content-type':'application/caprise+json'})
    res = client.get('/api/schemas/{0}/resources'.format(schema_id))
    resources = json.loads(res.data.decode('utf-8'))['resources']
    assert len(resources) == 2
    res = client.get('/api/schemas/{0}/resources'.format(another_schema_id))
    resources = json.loads(res.data.decode('utf-8'))['resources']
    assert len(resources) == 1

def test_resource_get(client):
    res = client.post(
            '/api/schemas', 
            data=json.dumps({'schema':1}), 
            headers={'content-type':'application/json'})
    schema_id = json.loads(res.data.decode('utf-8'))['id']

    resource = {'resource':1}
    res = client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=json.dumps(resource), 
            headers={'content-type':'application/caprise+json'})
    res = client.get(
            '/api/schemas/{0}/resources/{1}'.format(
                schema_id,
                json.loads(res.data.decode('utf-8'))['id']))
    assert res.status_code == 200
    assert json.loads(res.data.decode('utf-8')) == resource

    resource = {'resource':2}
    resource_id = 'testget'
    res = client.put(
            '/api/schemas/{0}/resources/{1}'.format(schema_id, resource_id),
            data=json.dumps(resource), 
            headers={'content-type':'application/caprise+json'})
    res = client.get(
            '/api/schemas/{0}/resources/{1}'.format(
                schema_id,
                resource_id))
    assert res.status_code == 200
    assert json.loads(res.data.decode('utf-8')) == resource

def test_resource_delete(client):
    res = client.post(
            '/api/schemas', 
            data=json.dumps({'schema':1}), 
            headers={'content-type':'application/json'})
    schema_id = json.loads(res.data.decode('utf-8'))['id']

    resource_id = 'notfoundresource'
    res = client.delete('/api/schemas/{0}/resources/{1}'.format(schema_id, resource_id))
    assert res.status_code == 404
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': "Resource isn't found."}})

    resource_id = 'foundresource'
    res = client.put(
            '/api/schemas/{0}/resources/{1}'.format(schema_id, resource_id),
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/caprise+json'})
    res = client.delete('/api/schemas/{0}/resources/{1}'.format(schema_id, resource_id))
    assert res.status_code == 204
    res = client.delete('/api/schemas/{0}/resources/{1}'.format(schema_id, resource_id))
    assert res.status_code == 404
    assert (json.loads(res.data.decode('utf-8')) 
            == {'error': {'message': "Resource isn't found."}})
