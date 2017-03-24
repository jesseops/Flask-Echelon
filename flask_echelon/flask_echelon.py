# -*- coding: utf-8 -*-


from flask import current_app


class EchelonManager:
    """
    Echelon Manager

    Simple Flask Plugin which provides a hierarchical
    approach to managing Flask application permissions.
    """
    def __init__(self, app=None, database=None, collection='echelons', separator='::'):
        self._db = database
        self._separator = separator
        self._mongo_collection = collection
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.echelon_manager = self

    @property
    def db(self):
        if not self._db:
            return current_app.db
        return self._db
