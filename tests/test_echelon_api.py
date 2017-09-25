#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_echelon_api.py
----------------------------------

Tests for `api` module.
"""

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


def test_000_init(client):
    assert 'echelon api' in client.get('/api/').data.decode().lower()


def test_001_GET_echelon_list(client):
    client.get('/api/echelons')
