#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_echelon_api.py
----------------------------------

Tests for `api` module.
"""
import json
from uuid import uuid4

import pytest
from flask import Flask
from pymongo import MongoClient

from flask_echelon import EchelonManager

# only use one MongoClient instance
DB = MongoClient().test_flask_echelon


def setup_function(function):
    DB.echelons.drop()


def teardown_function(function):
    DB.echelons.drop()


# Util functions

def get_response_json(response):
    return json.loads(response.data.decode('utf8'))


# End util functions


@pytest.fixture
def app():
    mc = MongoClient()
    db = mc[str(uuid4())]
    app = Flask(__name__)
    EchelonManager(app, database=db, api_url_prefix='/api')
    yield app
    mc.drop_database(db.name)


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def foo(app):
    app.echelon_manager.define_echelon('foo')
    return app.echelon_manager.get_echelon('foo')


def test_000_init(client):
    assert 'echelon' in client.get('/api/').data.decode().lower()


def test_001_list_echelons(client, foo):
    response = get_response_json(client.get('/api/echelons'))
    assert isinstance(response, list)
    assert len(response) == 1
    assert isinstance(response[0], dict)


def test_002_show_echelon(client, foo):
    e = get_response_json(client.get(f'/api/echelons/{foo["echelon"]}'))
    assert foo['echelon'] == e['echelon']
    assert 'users' in e
    assert 'groups' in e


@pytest.mark.parametrize('echelon_name,echelon_request,valid',
                         [('1', {'echelon': '1', 'name': '1!', 'help': '1!'}, True),
                          ('2', {'echelon': '2', 'name': '2!'}, True),
                          ('3', {'echelon': '3'}, True),
                          ('4', {}, True),
                          ('5', {'echelon': 'not5'}, False),
                          ('6', {'users': ['john117', 'kelly087', 'dutch', 'mickey']}, True),
                          ('7', {'groups': ['spartans', 'odst']}, True)])
def test_003_create_echelon(client, echelon_name, echelon_request, valid):

    assert client.get(f'/api/echelons/{echelon_name}').status_code == 404

    create_result = client.put(f'/api/echelons/{echelon_name}',
                               data=json.dumps(echelon_request),
                               headers={'Content-Type': 'application/json'})

    if not valid:
        assert create_result.status_code == 400, create_result.data.decode('utf8')
        return

    assert create_result.status_code == 201

    get_result = client.get(f'/api/echelons/{echelon_name}')
    assert get_result.status_code == 200

    e = get_response_json(get_result)
    assert e['echelon'] == echelon_name
    assert e['groups'] == echelon_request.get('groups', [])
    assert e['users'] == echelon_request.get('users', [])


def test_004_edit_echelon(client, foo):
    resource = f'/api/echelons/{foo["echelon"]}'
    client.post(resource,
                data=json.dumps({'add': {'users': ['john117']}}),
                headers={'Content-Type': 'application/json'})

    assert 'john117' in get_response_json(client.get(resource))['users']

    client.post(resource,
                data=json.dumps({'remove': {'users': ['john117']}}),
                headers={'Content-Type': 'application/json'})

    assert get_response_json(client.get(resource))['users'] == []


def test_005_delete_echelon(client, foo):
    client.delete(f'/api/echelons/{foo["echelon"]}')
    assert client.get(f'/api/echelons/{foo["echelon"]}').status_code == 404


if __name__ == '__main__':
    pytest.main()
