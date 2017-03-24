#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_flask_echelon
----------------------------------

Tests for `flask_echelon` module.
"""

import pytest


from flask import Flask
from flask_echelon import EchelonManager


def test_000_init():
    """Can be initialized as a Flask plugin or standalone"""
    EchelonManager()
    EchelonManager(app=Flask(__name__))
