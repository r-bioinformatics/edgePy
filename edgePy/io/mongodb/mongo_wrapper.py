"""
A simple library for wrapping around mongo collections and access issues.
"""

import pymongo
from pymongo.errors import BulkWriteError
from pymongo import InsertOne, UpdateOne


class MongoWrapper(object):

    def __init__(self, host, port, connect=True, verbose=False):
        self.host = host
        self.port = int(port)
        self.session = pymongo.MongoClient(host=self.host, port=self.port, connect=connect)
        self.verbose = verbose

    def find_as_cursor(self, database, collection, query=None, projection=None):
        mongo_db = self.session[database][collection]
        try:
            cursor = mongo_db.find(query, projection)
        except Exception as exception:
            print(exception)
            raise Exception("Mongo find failed")

        return cursor

    def find_as_list(self, database, collection, query=None, projection=None):
        cursor = self.find_as_cursor(database=database, collection=collection, query=query, projection=projection)
        return [c for c in cursor]

    def find_as_dict(self, database, collection, query, field='_id', projection=None):
        cursor = self.find_as_cursor(database=database, collection=collection, query=query, projection=projection)
        return {c[field]: c for c in cursor}

    def insert(self, database, collection, data_list):
        mongo_db = self.session[database][collection]
        try:
            mongo_db.test.insert_many(data_list, ordered=False)
        except BulkWriteError as bwe:
            print(bwe.details)

    def create_index(self, database, collection, key):
        self.session[database][collection].create_index(key)


class MongoInserter(MongoWrapper):

    def __init__(self, host, port, database, collection, connect=True):
        MongoWrapper.__init__(self, host, port, connect=connect)
        self.database = database
        self.collection = collection
        self.to_insert = []
        self.mongo_col = self.session[database][collection]

    def flush(self):
        if self.to_insert:
            try:
                result = self.mongo_col.bulk_write(self.to_insert, ordered=False)
                if result and self.verbose:
                    print(result.bulk_api_result)
            except BulkWriteError as bwe:
                print(bwe.details)
                raise Exception("Mongo bulk write failed.")
        del self.to_insert[:]

    def add(self, record):
        self.to_insert.append(InsertOne(record))
        if len(self.to_insert) > 1000:
            self.flush()

    def close(self):
        self.flush()

    def create_index_key(self, key):
        self.create_index(self.database, self.collection, key)


class MongoUpdater(MongoWrapper):

    def __init__(self, host, port, database, collection, connect=True):
        MongoWrapper.__init__(self, host, port, connect=connect)
        self.database = database
        self.to_update = []
        self.mongo_col = self.session[database][collection]

    def flush(self):
        if self.to_update:
            try:
                result = self.mongo_col.bulk_write(self.to_update, ordered=False)
                if result and self.verbose:
                    print(result.bulk_api_result)
            except BulkWriteError as bwe:
                print(bwe.details)
                raise Exception("Mongo bulk write failed.")
        del self.to_update[:]

    def add(self, updatedict, setdict):
        self.to_update.append(UpdateOne(updatedict, setdict))
        if len(self.to_update) > 1000:
            self.flush()

    def close(self):
        self.flush()
