"""
A simple library for wrapping around mongo collections and access issues.
"""
from typing import Dict, Hashable, Any, Iterable, List, Union

import pymongo  # type: ignore
from pymongo.errors import BulkWriteError  # type: ignore
from pymongo import InsertOne, UpdateOne

from edgePy.util import LOG as log  # type: ignore


class MongoWrapper(object):
    """This class is for use as a thin layer for interactinvg with the Mongo Database
    using pymongo. Pymongo is an entirely reasonable way of working with Mongodb, but
    fails to provide some very common functions that are frequently used.

    This class should be used for efficient retrieval of information from the database.

    Args:
        host: the name of the machine hosting the database
        port: the port number (usually 27017
        connect: whether to create the new session, or to attach to an existing session,
            set to false, if this is being instantiated by a subprocesses.
        verbose: suppresses output, when set to false.

    """

    def __init__(
        self, host: str, port: Union[str, int] = 27017, connect: bool = True, verbose: bool = False
    ) -> None:
        self.host = host
        self.port = int(port)
        self.session = pymongo.MongoClient(host=self.host, port=self.port, connect=connect)
        self.verbose = verbose

    def get_db(self, database: str, collection: str) -> Any:
        """
        This function simply hides the db name when using pytest-mongodb, when the database name
        should always be 'pytest'
        :param database:  database name
        :param collection:  collection name
        :return: the collection object ready for use with .find() or similar.
        """

        if database == "pytest":
            return self.session[collection]
        else:
            return self.session[database][collection]

    def find_as_cursor(
        self,
        database: str,
        collection: str,
        query: Dict[Hashable, Any] = None,
        projection: Dict[Hashable, Any] = None,
    ) -> Iterable:
        """
        Do a find operation on a mongo collection and return the data as a cursor,
        the (native MongoClient find return type.)
        :param database: db name
        :param collection: collection name
        :param query: a dictionary providing the criteria for the find command
        :param projection: a dictionary that gives the projection - the fields to return.
        :return: a cursor object, to be used as an iterator.
        """

        try:
            cursor = self.get_db(database, collection).find(query, projection)
        except Exception as exception:
            log.exception(exception)
            raise Exception("Mongo find failed")

        return cursor

    def find_as_list(
        self,
        database: str,
        collection: str,
        query: Dict[Hashable, Any] = None,
        projection: Dict[Hashable, Any] = None,
    ) -> Iterable:
        """
        Do a find operation on a mongo collection, but return the data as a list
        :param database: db name
        :param collection: collection name
        :param query: a dictionary providing the criteria for the find command
        :param projection: a dictionary that gives the projection - the fields to return.
        :return: a list representation of the returned data.
        """
        cursor = self.find_as_cursor(
            database=database, collection=collection, query=query, projection=projection
        )
        return [c for c in cursor]

    def find_as_dict(
        self,
        database: str,
        collection: str,
        query: Dict[Hashable, Any] = None,
        field: str = "_id",
        projection: Dict[Hashable, Any] = None,
    ) -> Iterable:
        """
         Do a find operation on a mongo collection, but return the data as a dictionary
        :param database: db name
        :param collection: collection name
        :param query: a dictionary providing the criteria for the find command
        :param projection: a dictionary that gives the projection - the fields to return.
        :param field: the field in the projection for which the value will be used as the Hashable key of the dict.
        :return: a dictionary representation of the returned data.
        """
        cursor = self.find_as_cursor(
            database=database, collection=collection, query=query, projection=projection
        )
        return {c[field]: c for c in cursor}

    def insert(self, database: str, collection: str, data_list: List[Any]) -> None:
        """
        bulk insert of items into a mongodb collection.
        :param database: db name
        :param collection: collection name
        :param data_list: a list of documents to insert into mongodb.
        :return: None
        """

        try:
            self.get_db(database, collection).test.insert_many(data_list, ordered=False)
        except BulkWriteError as bwe:
            log.exception(bwe.details)

    def create_index(self, database: str, collection: str, key: str) -> None:

        """
        A tool for creating indexes on a given collection.
        :param database: db name
        :param collection: collection name
        :param key: the field name to create the index on.
        :return: None
        """
        self.get_db(database, collection).create_index(key)


class MongoInserter(MongoWrapper):
    """

    This class is a thin layer on the MongoWrapper class, which is a thin layer on the pymongo library.
    It is used for instances where you want to insert data into a mongodb collection.  It creates
    a buffer which is periodically flushed to Mongo.

    Args:
        host: the name of the machine hosting the database
        port: the port number (usually 27017)
        database: db name
        collection: collection name
        connect: whether to create the new session, or to attach to an existing session,
            set to false, if this is being instantiated by a subprocesses.

    """

    def __init__(
        self, host: str, port: int, database: str, collection: str, connect: bool = True
    ) -> None:
        MongoWrapper.__init__(self, host, port, connect=connect)
        self.database = database
        self.collection = collection
        self.to_insert: List = []
        self.mongo_col = self.get_db(database, collection)

    def flush(self) -> None:
        """
        Flush out the buffer and write to mongo db.
        :return: None
        """
        if self.to_insert:
            try:
                result = self.mongo_col.bulk_write(self.to_insert, ordered=False)
                if result and self.verbose:
                    log.info(result.bulk_api_result)
            except BulkWriteError as bwe:
                log.exception(bwe.details)
                raise Exception("Mongo bulk write failed.")
        del self.to_insert[:]

    def add(self, record: Union[List[Any], Dict[Hashable, Any]]) -> None:
        """
        Add a record to the buffer
        :param record:
        :return: None
        """
        self.to_insert.append(InsertOne(record))
        if len(self.to_insert) > 1000:
            self.flush()

    def close(self) -> None:
        """
        Close the MongoInserter - flush the buffer.
        :return: None
        """

        self.flush()

    def create_index_key(self, key: str) -> None:
        """
        A tool for creating indexes on the collection.
        :return:
        """
        self.create_index(self.database, self.collection, key)


class MongoUpdater(MongoWrapper):
    """

        This class is a thin layer on the MongoWrapper class, which is a thin layer on the pymongo library.
        It is used for instances where you want to Update data in a mongodb collection.  It creates
        a buffer which is periodically flushed  and written to mongo.

        Args:
            host: the name of the machine hosting the database
            port: the port number (usually 27017
            database: db name
            collection: collection name
            connect: whether to create the new session, or to attach to an existing session,
                set to false, if this is being instantiated by a subprocesses.

        """

    def __init__(
        self, host: str, port: int, database: str, collection: str, connect: bool = True
    ) -> None:
        MongoWrapper.__init__(self, host, port, connect=connect)
        self.database = database
        self.to_update: List[Any] = []
        self.mongo_col = self.get_db(database, collection)

    def flush(self) -> None:
        """
        Flush out the buffer and write to mongo db.
        :return: None
        """
        if self.to_update:
            try:
                result = self.mongo_col.bulk_write(self.to_update, ordered=False)
                if result and self.verbose:
                    log.info(result.bulk_api_result)
            except BulkWriteError as bwe:
                log.exception(bwe.details)
                raise Exception("Mongo bulk write failed.")
        del self.to_update[:]

    def add(self, updatedict: Dict[Hashable, Any], setdict: Dict[Hashable, Any]) -> None:
        """
        Add a record to the buffer
        :param updatedict: the criteria for the update query
        :param setdict: the dictionary describing the new record - OR use {$set: {}} to update a
            particular key without replacing the existing record.
        :return: None
        """

        self.to_update.append(UpdateOne(updatedict, setdict))
        if len(self.to_update) > 1000:
            self.flush()

    def close(self) -> None:
        """
        Close the MongoInserter - flush the buffer.
        :return: None
        """
        self.flush()
