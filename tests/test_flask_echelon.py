#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_flask_echelon
----------------------------------

Tests for `flask_echelon` module.
"""

import pytest
from flask import Flask, _request_ctx_stack
from flask_login import AnonymousUserMixin, LoginManager, UserMixin
from pymongo import MongoClient

from flask_echelon import AccessCheckFailed, EchelonManager, MemberTypes
from flask_echelon.helpers import has_access, require_echelon

# only use one MongoClient instance
DB = MongoClient().test_flask_echelon


class User(UserMixin):
    """Mocks Flask-Login User"""

    def __init__(self, user_id, groups):
        self.id = user_id
        self._groups = groups

    @property
    def groups(self):
        return self._groups


class AnonUser(AnonymousUserMixin):
    """Mocks Flask-Login Anon User"""

    def __init__(self, id):
        self.id = id


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

    with pytest.raises(Exception):
        manager.add_member(echelon, 'testuser')

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


def test_014_invalid_echelon():
    manager = EchelonManager(database=DB)
    user = User('test', [])

    with pytest.raises(ValueError):
        manager.define_echelon('::foo::bar')
    with pytest.raises(ValueError):
        manager.check_access(user, '::foo::bar')


def test_015_all_echelons():
    echelons = ['flask::admin', 'flask::user', 'flask', 'foo', 'bar::baz']
    manager = EchelonManager(database=DB)
    for e in echelons:
        manager.define_echelon(e)
    assert set(echelons) == set(manager.all_echelons.keys())


def test_016_anonymous():
    manager = EchelonManager(database=DB)
    manager.define_echelon('anon')
    user = AnonUser('anonymous')
    manager.add_member('anon', user.get_id(), MemberTypes.USER)

    assert manager.check_access(user, 'anon') is True


def test_017_compile_echelons_user():
    manager = EchelonManager(database=DB)
    manager.define_echelon('foo::bar')
    manager.define_echelon('foo')
    manager.define_echelon('ham::spam::eggs')
    manager.define_echelon('spam::spam::spam')
    user = User('user1', ['group1', 'group2'])
    manager.add_member('foo', user.get_id(), MemberTypes.USER)
    manager.add_member('ham::spam::eggs', user.get_id(), MemberTypes.USER)
    access = manager.member_echelons(user, member_type=MemberTypes.USER)
    assert 'foo' in access
    assert 'foo::bar' in access
    assert 'spam' not in access
    assert 'spam::spam::spam' not in access


def test_018_compile_echelons_group():
    manager = EchelonManager(database=DB)
    manager.define_echelon('foo::bar')
    manager.define_echelon('foo')
    manager.define_echelon('ham::spam::eggs')
    manager.define_echelon('spam::spam::spam')
    manager.add_member('foo', 'group1', MemberTypes.GROUP)
    manager.add_member('ham::spam::eggs', 'group1', MemberTypes.GROUP)
    access = manager.member_echelons('group1', member_type=MemberTypes.GROUP)
    assert 'foo' in access
    assert 'foo::bar' in access
    assert 'spam' not in access
    assert 'spam::spam::spam' not in access


def test_019_helper_has_access():
    app = Flask(__name__)
    LoginManager(app)
    manager = EchelonManager(app, database=DB)

    manager.define_echelon('foo::bar')
    manager.define_echelon('foo')
    manager.define_echelon('spam::spam::spam')

    user = User('user1', ['group1'])
    manager.add_member('foo', user.get_id(), MemberTypes.USER)

    with app.test_request_context():
        _request_ctx_stack.top.user = user
        assert has_access('foo::bar')
        assert not has_access('spam::spam::spam')


def test_020_helper_require_echelon():
    app = Flask(__name__)
    LoginManager(app)
    manager = EchelonManager(app, database=DB)

    manager.define_echelon('foo::bar')
    manager.define_echelon('foo')
    manager.define_echelon('spam')

    user = User('user1', ['group1'])
    manager.add_member('spam', user.get_id(), MemberTypes.USER)

    @require_echelon('foo')
    def foo():
        return 'bar'

    @require_echelon('spam::spam::spam')
    def spam():
        return 'spam'

    with app.test_request_context():
        _request_ctx_stack.top.user = user
        with pytest.raises(AccessCheckFailed):
            foo()
        spam()


def test_020_helper_unbound():
    app = Flask(__name__)
    user = User('user1', ['group1'])
    with app.test_request_context():
        _request_ctx_stack.top.user = user
        with pytest.raises(Exception):
            assert has_access('foo')


def test_021__is_member():
    manager = EchelonManager(database=DB)
    manager.define_echelon('foo::bar')
    manager.define_echelon('foo')
    manager.define_echelon('ham::spam::eggs')
    manager.define_echelon('spam::spam::spam')
    manager.add_member('foo', 'group1', MemberTypes.GROUP)
    manager.add_member('ham::spam::eggs', 'group1', MemberTypes.GROUP)
    access = manager.member_echelons('group1', member_type=MemberTypes.GROUP)
    assert 'foo' in access
    assert 'foo::bar' in access
    assert 'spam' not in access
    assert 'spam::spam::spam' not in access


if __name__ == "__main__":
    pytest.main()
