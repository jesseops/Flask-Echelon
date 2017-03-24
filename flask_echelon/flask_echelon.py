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
            self.app = app
            self.init_app(app)

    def init_app(self, app):
        self.db[self._mongo_collection].create_index("echelon", unique=True)
        app.echelon_manager = self

    def define_echelon(self, echelon, name=None, help=None):
        """
        Creates or updates an Echelon definition

        :param echelon: (str) Representation of a single Echelon within
        a permission hierarchy
        :param name: (str) Pretty name for a given Echelon
        :param help: (str) Help text defining Echelon purpose/scope
        :return: None
        """
        if echelon.startswith(self._separator):
            raise Exception('{} leads with separator "{}"'.format(echelon, self._separator))

        init = {'groups': [], 'users': []}

        payload = {"echelon": echelon,
                   "name": name or echelon,
                   "help": help or "Provides access to {}".format(echelon)}

        self.db[self._mongo_collection].update({"echelon": echelon},
                                               {"$set": payload, "$setOnInsert": init},
                                               upsert=True)

    @property
    def db(self):
        if self._db is not None:
            return self._db
        if self.app:
            try:
                return self.app.db
            except AttributeError:
                raise Exception('No database defined on manager or current_app')
