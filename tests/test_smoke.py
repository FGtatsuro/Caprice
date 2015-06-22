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

def test_resource(client):
    res = client.get('/api/resources', follow_redirects=True)
    assert res.status_code == 200

    res = client.post('/api/resources', follow_redirects=True)
    assert res.status_code == 201

def test_lock(client):
    res = client.get('/api/locks', follow_redirects=True)
    assert res.status_code == 200

    res = client.post('/api/locks', follow_redirects=True)
    assert res.status_code == 201
