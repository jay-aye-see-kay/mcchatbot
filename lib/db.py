import sqlite3
from abc import ABC
from datetime import datetime

from lib.config import Config


class BaseEvent(ABC):
    """methods to share between all events"""

    time: datetime

    def columns(self):
        return [k for k in self.__dict__.keys() if not k.startswith("_")]

    def table_name(self):
        return self.__class__.__name__

    def sql_create_table(self):
        columns = ", ".join(self.columns())
        return f"CREATE TABLE IF NOT EXISTS {self.table_name()}({columns})"

    def sql_insert_row(self):
        template = ", ".join(["?"] * len(self.columns()))
        return (
            f"INSERT INTO {self.table_name()} VALUES ({template})",
            tuple(getattr(self, k) for k in self.columns()),
        )


def init_db(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con
