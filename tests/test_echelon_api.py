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
    response = client.get('/api/echelons')


def test_002_show_echelon(client, foo):
    e = get_response_json(client.get(f'/api/echelons/{foo["echelon"]}'))
    assert foo['echelon'] == e['echelon']


def test_003_create_echelon(client):
    pass


def test_004_edit_echelon(client):
    pass


def test_005_delete_echelon(client):
    pass


def get_response_json(response):
    return json.loads(response.data.decode('utf8'))


if __name__ == '__main__':
    pytest.main()
