import unittest
from datetime import datetime

from lib.ai_complete import format_ai_message
from lib.config import Config, test_config
from lib.events import LogEvent


class TestSavingEventsToDb(unittest.TestCase):
    def test_format_ai_message(self):
        expected = """Here is a list of previous logs and messages in the conversation:
at "10:11:12" user_1 said "hey"
at "10:11:13" user_2 said "h1"
"""
        actual = format_ai_message(
            test_config,
            [
                LogEvent(
                    "Message",
                    datetime.strptime("10:11:12", "%H:%M:%S"),
                    "user_1",
                    "hey",
                ),
                LogEvent(
                    "Message",
                    datetime.strptime("10:11:13", "%H:%M:%S"),
                    "user_2",
                    "h1",
                ),
            ],
        )
        self.assertEqual(actual, expected)

    def test_format_ai_message_replaces_names(self):
        test_config = Config(test=True)
        test_config.replace_names = test_config.parse_replace_names("user_1=John")

        expected = """Here is a list of previous logs and messages in the conversation:
at "10:11:12" John said "hey"
"""
        actual = format_ai_message(
            test_config,
            [
                LogEvent(
                    "Message",
                    datetime.strptime("10:11:12", "%H:%M:%S"),
                    "user_1",
                    "hey",
                ),
            ],
        )
        self.assertEqual(actual, expected)
