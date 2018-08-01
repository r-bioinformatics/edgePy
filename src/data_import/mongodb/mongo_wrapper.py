"""
A simple library for wrapping around mongo collections and access issues.
"""

import pymongo  # type: ignore
from pymongo.errors import BulkWriteError
from pymongo import InsertOne, UpdateOne
from typing import Dict, Hashable, Any, Iterable, List, Union


class MongoWrapper(object):

    def __init__(self, host: str, port: int, connect: bool=True, verbose: bool=False) -> None:
        self.host = host
        self.port = int(port)
        self.session = pymongo.MongoClient(host=self.host, port=self.port, connect=connect)
        self.verbose = verbose

    def find_as_cursor(self, database: str, collection: str, query: Dict[Hashable, Any]=None,
                       projection: Dict[Hashable, Any]=None) -> Iterable:

        mongo_db = self.session[database][collection]
        try:
            cursor = mongo_db.find(query, projection)
        except Exception as exception:
            print(exception)
            raise Exception("Mongo find failed")

        return cursor

    def find_as_list(self, database: str, collection: str, query: Dict[Hashable, Any]=None,
                       projection: Dict[Hashable, Any]=None) -> Iterable:
        cursor = self.find_as_cursor(database=database, collection=collection, query=query, projection=projection)
        return [c for c in cursor]

    def find_as_dict(self, database: str, collection: str, query: Dict[Hashable, Any]=None, field='_id',
                       projection: Dict[Hashable, Any]=None) -> Iterable:
        cursor = self.find_as_cursor(database=database, collection=collection, query=query, projection=projection)
        return {c[field]: c for c in cursor}

    def insert(self, database: str, collection: str, data_list: List[Any]) -> None:
        mongo_db = self.session[database][collection]
        try:
            mongo_db.test.insert_many(data_list, ordered=False)
        except BulkWriteError as bwe:
            print(bwe.details)

    def create_index(self, database: str, collection: str, key: str) -> None:
        self.session[database][collection].create_index(key)


class MongoInserter(MongoWrapper):

    def __init__(self, host: str, port: int, database: str, collection: str, connect: bool=True) -> None:
        MongoWrapper.__init__(self, host, port, connect=connect)
        self.database = database
        self.collection = collection
        self.to_insert: List = []
        self.mongo_col = self.session[database][collection]

    def flush(self) -> None:
        if self.to_insert:
            try:
                result = self.mongo_col.bulk_write(self.to_insert, ordered=False)
                if result and self.verbose:
                    print(result.bulk_api_result)
            except BulkWriteError as bwe:
                print(bwe.details)
                raise Exception("Mongo bulk write failed.")
        del self.to_insert[:]

    def add(self, record: Union[List[Any], Dict[Hashable, Any]]) -> None:
        self.to_insert.append(InsertOne(record))
        if len(self.to_insert) > 1000:
            self.flush()

    def close(self) -> None:
        self.flush()

    def create_index_key(self, key: str) -> None:
        self.create_index(self.database, self.collection, key)


class MongoUpdater(MongoWrapper):

    def __init__(self, host: str, port: int, database: str, collection: str, connect: bool=True) -> None:
        MongoWrapper.__init__(self, host, port, connect=connect)
        self.database = database
        self.to_update: List[Any] = []
        self.mongo_col = self.session[database][collection]

    def flush(self) -> None:
        if self.to_update:
            try:
                result = self.mongo_col.bulk_write(self.to_update, ordered=False)
                if result and self.verbose:
                    print(result.bulk_api_result)
            except BulkWriteError as bwe:
                print(bwe.details)
                raise Exception("Mongo bulk write failed.")
        del self.to_update[:]

    def add(self, updatedict: Dict[Hashable, Any], setdict: Dict[Hashable, Any]) -> None:
        self.to_update.append(UpdateOne(updatedict, setdict))
        if len(self.to_update) > 1000:
            self.flush()

    def close(self) -> None:
        self.flush()
