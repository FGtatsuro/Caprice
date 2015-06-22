#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from caprice import _create_app

@pytest.fixture
def client(request):
    class TestConfig(object):
        TESTING = True
    app = _create_app(TestConfig)
    client = app.test_client()
    return client

def test_schema(client):
    res = client.get('/api/schemas', follow_redirects=True)
    assert res.status_code == 200
    res = client.post('/api/schemas', follow_redirects=True)
    assert res.status_code == 201

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
