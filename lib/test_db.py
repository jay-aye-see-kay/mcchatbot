import copy
import unittest
from datetime import datetime

from lib.config import testConfig
from lib.db import ensure_db_setup, init_db, query_context_messages, save_event
from lib.events import LogEvent

test_events: list[LogEvent] = [
    LogEvent("Message", datetime.now(), "me", "hi"),
    LogEvent("Join", datetime.now(), "me", ""),
    LogEvent("Leave", datetime.now(), "me", ""),
    LogEvent("Death", datetime.now(), "me", "drowned"),
    LogEvent("GameMode", datetime.now(), "me", "Survival Mode"),
]


class TestSavingEventsToDb(unittest.TestCase):
    def test_save_and_read(self):
        for event in test_events:
            with self.subTest(event=event):
                db = init_db(testConfig)
                ensure_db_setup(db)
                save_event(db, event)
                msg_from_db = LogEvent(*db.execute("select * from events").fetchone())
                self.assertEqual(event, msg_from_db)

    def test_query_context_messages(self):
        cfg = copy.deepcopy(testConfig)
        cfg.context_message_limit = 3
        db = init_db(cfg)
        ensure_db_setup(db)
        for event in test_events:
            save_event(db, event)
        messages = query_context_messages(cfg, db)

        # should limit returned results
        self.assertEqual(len(messages), cfg.context_message_limit)
        # should sort oldest first, but truncate away oldest messages
        self.assertEqual(messages[0], test_events[2])
        self.assertEqual(messages[1], test_events[3])
        self.assertEqual(messages[2], test_events[4])
