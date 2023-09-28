import unittest

from lib.db import init_db
from lib.db_setup import dummy_events, ensure_db_setup


class TestSavingEventsToDb(unittest.TestCase):
    def test_save_and_read(self):
        for event in dummy_events:
            with self.subTest(event=event):
                db = init_db(":memory:")
                ensure_db_setup(db)
                db.execute(*event.sql_insert_row())
                msg_from_db = event.__class__(
                    *db.execute(f"select * from {event.table_name()}").fetchone()
                )
                self.assertEqual(event, msg_from_db)
