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


class User:
    def __init__(self, user_id, groups):
        self._id = user_id
        self._groups = groups

    @property
    def groups(self):
        return self._groups

    def get_id(self):
        return self._id


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


def test_001_define_echelon():
    """Can define interactions successfully"""
    manager = EchelonManager(database=DB)
    echelon = "foo::bar::baz"
    manager.define_echelon(echelon, name="I test things", help="It's a test, ok?")


def test_002_access_echelon(foobarbaz):
    manager, echelon = foobarbaz

    assert manager.get_echelon(echelon) is not None
    assert echelon in manager.all_echelons


def test_003_update_echelon(foobarbaz):
    """Can update a given interaction in place"""
    manager, echelon = foobarbaz

    manager.define_echelon(echelon, name="I just changed", help="Me too!")

    assert 'just changed' in manager.get_echelon(echelon)['name']
    assert len(manager.all_echelons.values()) == 1


def test_004_remove_echelon(foobarbaz):
    manager, echelon = foobarbaz

    assert manager.get_echelon(echelon) is not None
    assert echelon in manager.all_echelons

    manager.remove_echelon(echelon)

    assert manager.get_echelon(echelon) is None
    assert echelon not in manager.all_echelons


def test_005_add_member(foobarbaz):
    manager, echelon = foobarbaz

    manager.add_member(echelon, 'testuser', MemberTypes.USER)
    assert 'testuser' in manager.get_echelon(echelon)['users']


def test_006_remove_member(foobarbaz):
    manager, echelon = foobarbaz

    manager.add_member(echelon, 'valid', MemberTypes.GROUP)
    assert 'valid' in manager.get_echelon(echelon)['groups']

    manager.remove_member(echelon, 'valid', MemberTypes.GROUP)
    assert 'valid' not in manager.get_echelon(echelon)['groups']


def test_006_user_member_noaccess(foobarbaz):
    manager, echelon = foobarbaz

    user = User('test', [])

    assert manager.check_access(user, echelon) is False


def test_007_user_member_access(foobarbaz):
    manager, echelon = foobarbaz

    user = User('test', [])
    manager.add_member(echelon, user.get_id(), MemberTypes.USER)

    assert manager.check_access(user, echelon) is True


def test_008_group_member_noaccess(foobarbaz):
    manager, echelon = foobarbaz

    user = User('test', ['foo'])

    assert manager.check_access(user, echelon) is False


def test_010_group_member_access(foobarbaz):
    manager, echelon = foobarbaz

    user = User('test', ['foo'])
    manager.add_member(echelon, user.groups[0], MemberTypes.GROUP)

    assert manager.check_access(user, echelon) is True


def test_011_hierarchical_access(foobarbaz):
    manager, luser_echelon = foobarbaz

    sep = manager._separator

    admin_echelon = luser_echelon.split(sep)[0]
    manager.define_echelon(admin_echelon)

    admin = User('admin', [])
    luser = User('user', [])

    manager.add_member(admin_echelon, admin.get_id(), MemberTypes.USER)
    manager.add_member(luser_echelon, luser.get_id(), MemberTypes.USER)

    assert manager.check_access(admin, admin_echelon) is True
    assert manager.check_access(admin, luser_echelon) is True

    assert manager.check_access(luser, admin_echelon) is False
    assert manager.check_access(luser, luser_echelon) is True


def test_012_undefined_echelon(foobarbaz):
    manager, echelon = foobarbaz

    sep = manager._separator
    undefined = sep.join([echelon, 'undefined'])

    user = User('user', [])

    assert manager.check_access(user, undefined) is False

    manager.add_member(echelon, user.get_id(), MemberTypes.USER)

    assert manager.check_access(user, echelon) is True
    assert manager.check_access(user, undefined) is True


def test_013_custom_separator():
    manager = EchelonManager(database=DB, separator='|')

    admin_echelon = 'foo'
    valid_echelon = 'foo|bar'
    another_valid_echelon = 'foo|bar|baz'
    invalid_echelon = 'foo!bar'

    manager.define_echelon(admin_echelon)
    manager.define_echelon(valid_echelon)
    manager.define_echelon(invalid_echelon)

    admin = User('admin', [])

    manager.add_member(admin_echelon, 'admin', MemberTypes.USER)

    assert manager.check_access(admin, admin_echelon) is True
    assert manager.check_access(admin, valid_echelon) is True
    assert manager.check_access(admin, another_valid_echelon) is True
    assert manager.check_access(admin, invalid_echelon) is False
