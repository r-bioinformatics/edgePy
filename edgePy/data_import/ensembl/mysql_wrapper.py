"""
This will be a wrapper file for using mysql, to make queries easier.  I may eventually just replace this with
SQLAlchemy, but for the moment, it's probalby easiest just to make a simple library to handle this type of transaction.

"""

import pymysql
from typing import List
from pymysql.cursors import DictCursor


class MySQLWrapper(object):
    def __init__(
        self,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        database: str = None,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.connection = pymysql.connect(
            host=self.host,
            user=self.username,
            password=self.password,
            db=self.database,
            charset="utf8mb4",
            cursorclass=DictCursor,
        )

    def find_one(self, sql: str) -> object:
        with self.connection.cursor() as cursor:
            # Read a single record
            cursor.execute(sql)
            result = cursor.fetchone()
        return result

    def insert(self, sql: str) -> None:
        with self.connection.cursor() as cursor:
            # Create a new record
            cursor.execute(sql)
        self.connection.commit()

    def update(self) -> None:
        raise NotImplementedError

    def run_sql_query(self, sql: str) -> List:
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        return result

    def close(self) -> None:
        self.connection.close()
