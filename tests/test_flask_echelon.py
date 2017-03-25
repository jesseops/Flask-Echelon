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
from flask_echelon import EchelonManager, MemberTypes


# only use one MongoClient instance
DB = MongoClient().test_flask_echelon


@pytest.fixture
def foobarbaz():
    manager = EchelonManager(database=DB)
    echelon = "foo::bar::baz"
    manager.define_echelon(echelon, name="I test things", help="It's a test, ok?")
    return manager, echelon


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


def test_002_access(foobarbaz):
    manager, echelon = foobarbaz

    assert manager.get_echelon(echelon) is not None
    assert echelon in manager.all_echelons


def test_003_update(foobarbaz):
    """Can update a given interaction in place"""
    manager, echelon = foobarbaz

    manager.define_echelon(echelon, name="I just changed", help="Me too!")

    assert 'just changed' in manager.get_echelon(echelon)['name']
    assert len(manager.all_echelons.values()) == 1


def test_004_remove(foobarbaz):
    manager, echelon = foobarbaz

    assert manager.get_echelon(echelon) is not None
    assert echelon in manager.all_echelons

    manager.remove_echelon(echelon)

    assert manager.get_echelon(echelon) is None
    assert echelon not in manager.all_echelons


def test_005_addmember(foobarbaz):
    manager, echelon = foobarbaz

    manager.add_member(echelon, 'testuser', MemberTypes.USER)
    assert 'testuser' in manager.get_echelon(echelon)['users']
