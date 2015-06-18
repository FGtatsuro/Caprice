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

def test_index(client):
    res = client.get('/', follow_redirects=True)
    assert b'This is the index page.' in res.data