#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_echelon_api.py
----------------------------------

Tests for `api` module.
"""

import pytest

from flask import Flask
from pymongo import MongoClient
from flask_echelon.api import EchelonApi
from flask_echelon import EchelonManager, MemberTypes

# only use one MongoClient instance
DB = MongoClient().test_flask_echelon


def setup_function(function):
    DB.echelons.drop()


def teardown_function(function):
    DB.echelons.drop()


def test_000_init():
    """Can be initialized as a Flask plugin or standalone"""
    app = Flask(__name__)
    EchelonManager(app, database=DB)
    app.register_blueprint(EchelonApi)
    with app.test_client() as client:
        assert 'echelon api' in client.get('/echelon/').data.decode().lower()
