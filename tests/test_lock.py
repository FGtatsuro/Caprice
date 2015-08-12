#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import json

import pytest
from sqlalchemy.orm import joinedload

from caprice import _create_app
from caprice.models import Schema, Resource, Lock
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
    s.query(Lock).delete()
    s.commit()
    return client

def test_lock_registration(client):
    res = client.post(
            '/api/schemas', 
            data=json.dumps({'aaa':1}), 
            headers={'content-type':'application/json'})
    schema_id = json.loads(res.data.decode('utf-8'))['id']

    res = client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=json.dumps({'aaa':2}), 
            headers={'content-type':'application/json'})
    res = client.post(
            '/api/schemas/{0}/resources'.format(schema_id), 
            data=json.dumps({'aaa':3}), 
            headers={'content-type':'application/json'})

    # 'application/json'
    schema = Schema.query.options(joinedload(Schema.resources)).filter(Schema.id==schema_id).first()
    schema_resources = schema.resources
    for r in schema_resources:
        Session.expunge(r)
    res = client.post(
            '/api/locks',
            data=json.dumps({'resources': [r.id for r in schema_resources]}), 
            headers={'content-type':'application/json'})
    assert res.status_code == 201
    lock_id = json.loads(res.data.decode('utf-8'))['id']
    assert isinstance(lock_id, int)
    lock = Lock.query.filter(Lock.id==lock_id).first()
    assert lock
    assert lock.resources
    assert len(lock.resources) == 2
    assert lock.resources[0].json in [r.json for r in schema_resources]
    assert lock.resources[1].json in [r.json for r in schema_resources]
