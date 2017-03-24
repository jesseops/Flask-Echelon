#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_flask_echelon
----------------------------------

Tests for `flask_echelon` module.
"""

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


def test_000_init():
    """Can be initialized as a Flask plugin or standalone"""
    EchelonManager()
    with pytest.raises(Exception):
        EchelonManager(app=Flask(__name__))
    EchelonManager(app=Flask(__name__), database=DB)
    EchelonManager(database=DB)


def test_001_define():
    """Can define interactions successfully"""
    manager = EchelonManager(database=DB)
    echelon = "foo::bar::baz"
    manager.define_echelon(echelon, name="I test things", help="It's a test, ok?")


def test_002_access():
    manager = EchelonManager(database=DB)
    echelon = "foo::bar::baz"
    manager.define_echelon(echelon, name="I test things", help="It's a test, ok?")

    assert manager.get_echelon(echelon) is not None
    assert echelon in manager.all_echelons


def test_003_update():
    """Can update a given interaction in place"""
    manager = EchelonManager(database=DB)
    echelon = "foo::bar::baz"
    manager.define_echelon(echelon, name="I test things", help="It's a test, ok?")
    manager.define_echelon(echelon, name="I just changed", help="Me too!")

    assert 'just changed' in manager.get_echelon(echelon)['name']
    assert len(manager.all_echelons.values()) == 1
