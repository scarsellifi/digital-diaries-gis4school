"""
simple logging module
"""
import json
from sqlalchemy import text
from sqlalchemy.sql import func
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    DateTime,
    JSON,
)
from db import engine


class log_obj:
    "log class"

    def __init__(self, context=None):
        self.context = context

    def write(self, dictionary):
        "write log in db"
        data = [{"context": self.context, "json": json.dumps(dictionary)}]
        with engine.connect() as con:
            statement = text(
                """INSERT INTO log (context, data) VALUES (:context, :json)"""
            )
            for row_data in data:
                result = con.execute(statement, row_data)

        return result

    @staticmethod
    def create_db():
        "create table in db"
        meta = MetaData()
        log = Table(
            "log",
            meta,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("timestamp", DateTime(timezone=True), server_default=func.now()),
            Column("context", String(2000)),
            Column("data", JSON),
        )
        meta.create_all(engine)
        return "table created"
