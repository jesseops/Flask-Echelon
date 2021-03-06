# -*- coding: utf-8 -*-

__author__ = """Jesse Roberts"""
__email__ = 'jesse@jesseops.net'
__version__ = '0.1.0'

from enum import Enum


class MemberTypes(Enum):
    USER = 'users'
    GROUP = 'groups'


class AccessCheckFailed(Exception):
    pass


from .flask_echelon import EchelonManager, MemberTypes
