import unittest

from lib.config import Config


class TestReplaceNames(unittest.TestCase):
    def test_handles_empty_str(self):
        config = Config(test=True)
        self.assertEqual(
            config.parse_replace_names(""),
            {},
        )

    def test_handles_one_name(self):
        config = Config(test=True)
        self.assertEqual(
            config.parse_replace_names("Player_X=John"),
            {"Player_X": "John"},
        )

    def test_handles_two_names(self):
        config = Config(test=True)
        self.assertEqual(
            config.parse_replace_names("Player_X=John,Player_Y=Tom"),
            {"Player_X": "John", "Player_Y": "Tom"},
        )

    def test_handles_spaces_and_trailing_comma(self):
        config = Config(test=True)
        self.assertEqual(
            config.parse_replace_names("Player_X=John,  Player_Y= Tom, "),
            {"Player_X": "John", "Player_Y": "Tom"},
        )

    def test_invalid_returns_empty_dict_and_logs_error(self):
        with self.assertLogs(level="ERROR") as cm:
            config = Config(test=True)
            invalid_str = ",,,==,==,=,=,=,="
            self.assertEqual(config.parse_replace_names(invalid_str), {})
            self.assertEqual(len(cm.output), 1)
