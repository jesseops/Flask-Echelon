# -*- coding: utf-8 -*-


from . import MemberTypes
from .api import EchelonApi


class EchelonManager:
    """
    Echelon Manager

    Simple Flask Plugin which provides a hierarchical
    approach to managing Flask application permissions.
    """

    def __init__(self, app=None, database=None, collection='echelons', separator='::', api_url_prefix=None):
        self._db = database
        self._separator = separator
        self._mongo_collection = collection
        if app:
            self.app = app
            self.init_app(app, api_url_prefix)

    def init_app(self, app, api_url_prefix=None):
        self.db[self._mongo_collection].create_index('echelon', unique=True)
        app.echelon_manager = self
        app.register_blueprint(EchelonApi, url_prefix=api_url_prefix)

    def add_member(self, echelon, member, member_type):
        if member_type not in MemberTypes:
            raise TypeError('Got invalid argument for member_type: {}'.format(member_type))
        if not isinstance(member, str) and hasattr(member, '__iter__'):
            member = {'$each': member}
        payload = {'$addToSet': {member_type.value: member}}
        self.db[self._mongo_collection].update({'echelon': echelon}, payload)

    def remove_member(self, echelon, member, member_type):
        if member_type not in MemberTypes:
            raise TypeError('Got invalid argument for member_type: {}'.format(member_type))
        if isinstance(member, str):
            member = [member]
        payload = {'$pull': {member_type.value: {'$in': member}}}
        self.db[self._mongo_collection].update({'echelon': echelon}, payload)

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
            raise ValueError('{} leads with separator "{}"'.format(echelon, self._separator))

        init = {'groups': [], 'users': []}

        payload = {"echelon": echelon,
                   "name": name or echelon,
                   "help": help or "Provides access to {}".format(echelon)}

        self.db[self._mongo_collection].update({"echelon": echelon},
                                               {"$set": payload, "$setOnInsert": init},
                                               upsert=True)

    def get_echelon(self, echelon):
        """
        Retrieve full data for a given Echelon

        :param echelon: (str) Representation of a single Echelon within
        a permission hierarchy
        :return: dict
        """
        return self.db[self._mongo_collection].find_one({'echelon': echelon}, {'_id': 0})

    def remove_echelon(self, echelon):
        """
        Remove an Echelon from the database

        :param echelon: (str) Representation of a single Echelon within
        a permission hierarchy
        :return: None
        """
        self.db[self._mongo_collection].remove({'echelon': echelon})

    def check_access(self, member, echelon, member_type=MemberTypes.USER):
        """
        Verify if a user has access to an Echelon.

        Echelons are designed to be hierarchical, ie if Bob has
        access to admin::user he can access functions protected by an
        echelon called admin::user::create; while a user with
        access to admin::user::view would be able to view all users
        but not perform any modifications.

        This method does a top > bottom check as the most common use
        case is users with more general ie higher privilege levels.

        :param user: (`Flask_Login.User`)
        :param echelon: (str) Representation of a single point in a
        permission hierarchy
        :return: Bool
        """
        if echelon.startswith(self._separator):
            raise ValueError('{} leads with separator "{}"'.format(echelon, self._separator))
        hierarchy = echelon.split(self._separator)
        level = None

        while hierarchy:
            if level is not None:
                level = self._separator.join((level, hierarchy.pop(0)))
            else:
                level = hierarchy.pop(0)
            if self._is_member(member, level, member_type=member_type):
                return True
        return False

    def member_echelons(self, member, member_type):
        echelons = []
        for echelon in self.all_echelons:
            if self.check_access(member, echelon=echelon, member_type=member_type):
                echelons.append(echelon)
        return echelons

    @property
    def all_echelons(self):
        """
        Retrieve all Echelons as a dictionary where the top level key is
        the Echelon and the value is the data for the corresponding Echelon

        :return: dict
        """
        echelons = {}
        for echelon in self.db[self._mongo_collection].find({}, {'_id': 0}):
            echelons[echelon['echelon']] = echelon
        return echelons

    @property
    def db(self):
        """
        Access a database instance. Prioritizes a DB assigned
        to the `EchelonManager` instance, falling back to the
        previously initialized app if it exists.

        :return: `pymongo.MongoClient.Database`
        """
        if self._db is not None:
            return self._db
        if self.app:
            try:
                return self.app.db
            except AttributeError:
                pass  # We'll handle this failure at the end of the method
        raise Exception('No database defined on manager or current_app')

    def _is_member(self, member, level, member_type):
        if member_type is MemberTypes.USER:
            user_id = member.get_id()
            # Groups is not a default attribute, default to empty list
            user_groups = member.groups if hasattr(member, 'groups') else []

            query = {'echelon': level,
                     "$or": [
                         {'groups': {'$in': user_groups}},
                         {'users': {'$in': [user_id]}},
                     ]}
        elif member_type is MemberTypes.GROUP:
            query = {'echelon': level,
                     'groups': {'$in': [member]}}
        else:
            return False

        if self.db[self._mongo_collection].find_one(query, {'_id': 1}):
            return True
