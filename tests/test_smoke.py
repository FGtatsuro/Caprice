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

def test_resource(client):
    res = client.get('/api/resources', follow_redirects=True)
    assert res.status_code == 200
