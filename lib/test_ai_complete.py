import unittest
from datetime import datetime

from lib.ai_complete import format_ai_message
from lib.events import LogEvent


class TestSavingEventsToDb(unittest.TestCase):
    def test_format_ai_message(self):
        expected = """Here is a list of previous logs and messages in the conversation:
at "10:11:12" user said "hey"
at "10:11:13" user2 said "h1"
"""
        actual = format_ai_message(
            [
                LogEvent(
                    "Message",
                    datetime.strptime("10:11:12", "%H:%M:%S"),
                    "user",
                    "hey",
                ),
                LogEvent(
                    "Message",
                    datetime.strptime("10:11:13", "%H:%M:%S"),
                    "user2",
                    "h1",
                ),
            ]
        )
        self.assertEqual(actual, expected)
