import sqlite3
import unittest
from datetime import datetime

from lib.events import (DeathEvent, GameModeEvent, JoinEvent, LeaveEvent,
                        MessageEvent)

events = [
    MessageEvent(datetime.now(), "me", "hi"),
    JoinEvent(datetime.now(), "me"),
    LeaveEvent(datetime.now(), "me"),
    DeathEvent(datetime.now(), "me", "drowned"),
    GameModeEvent(datetime.now(), "me", "Survival Mode"),
]


def mem_db():
    cx = sqlite3.connect(":memory:")
    cx.row_factory = sqlite3.Row
    return cx.cursor()


class TestSavingEventsToDb(unittest.TestCase):
    def test_save_and_read(self):
        for event in events:
            with self.subTest(event=event):
                db = mem_db()
                db.execute(event.sql_create_table())
                db.execute(*event.sql_insert_row())
                msg_from_db = event.__class__(
                    *db.execute(f"select * from {event.table_name()}").fetchone()
                )
                self.assertEqual(event, msg_from_db)
