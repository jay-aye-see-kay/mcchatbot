import unittest
from datetime import datetime

from lib.events import LogEvent, is_death, parse_event, parse_time

# logs that should be ingored by `is_death()` (it doesn't see timestamps)
is_death_ignorable_logs = [
    "[player_XX: Set own game mode to Spectator Mode]",
    "Thread [RCON](2023-09-24_rcon.md) Client /127.0.0.1 started",
    "Thread RCON Client /127.0.0.1 shutting down",
    "player_XX lost connection: Disconnected",
    "player_XX left the game",
    "UUID of player Player_YY is 548724a6-ae80-41af-9144-f6a02ab27fcb",
    "Player_YY joined the game",
    "Player_YY[/172.19.0.4:60669] logged in with entity id 53844 at ([world]210.27267354636194, 167.5, -97.29571541611286)",  # noqa: E501
    "Villager EntityVillager['Farmer'/61310, uuid='a0772acd-e86c-44f5-ad3a-b21c26ad0a7e', l='ServerLevel[world]', x=220.30, y=179.00, z=-63.30, cpos=[13, -4], tl=395686, v=true] died, message: 'Farmer was slain by Zombie'",  # noqa: E501
]

# logs that we completely ignore
completely_ignored_logs = [
    "[13:37:11 INFO]: Thread [RCON](2023-09-24_rcon.md) Client /127.0.0.1 started",
    "[13:37:16 INFO]: Thread RCON Client /127.0.0.1 shutting down",
    "[13:37:18 INFO]: player_XX lost connection: Disconnected",
    "[13:39:00 INFO]: UUID of player Player_YY is 548724a6-ae80-41af-9144-f6a02ab27fcb",
    "[13:41:07 INFO]: Player_YY[/172.19.0.4:60669] logged in with entity id 53844 at ([world]210.27267354636194, 167.5, -97.29571541611286)",  # noqa: E501
    "[13:41:30 INFO]: Villager EntityVillager['Farmer'/61310, uuid='a0772acd-e86c-44f5-ad3a-b21c26ad0a7e', l='ServerLevel[world]', x=220.30, y=179.00, z=-63.30, cpos=[13, -4], tl=395686, v=true] died, message: 'Farmer was slain by Zombie'",  # noqa: E501
]


class TestIsDeath(unittest.TestCase):
    def test_ignores_villager(self):
        self.assertFalse(is_death("Villager blew up"))

    def test_ignores_other_logs(self):
        for log in is_death_ignorable_logs:
            with self.subTest(log=log):
                self.assertFalse(is_death(log))

    def test_true_on_death(self):
        self.assertTrue(is_death("Player_YY blew up"))


class TestParseEvent(unittest.TestCase):
    def test_ignores_other_logs(self):
        for log in completely_ignored_logs:
            with self.subTest(log=log):
                self.assertIs(parse_event(log), None)

    def test_join_event(self):
        self.assertEqual(
            parse_event("[13:37:07 INFO]: Player_YY joined the game"),
            LogEvent("Join", parse_time("13:37:07"), "Player_YY", ""),
        )

    def test_leave_event(self):
        self.assertEqual(
            parse_event("[13:37:07 INFO]: Player_YY left the game"),
            LogEvent("Leave", parse_time("13:37:07"), "Player_YY", ""),
        )

    def test_death_event(self):
        self.assertEqual(
            parse_event("[13:37:07 INFO]: Player_YY blew up"),
            LogEvent("Death", parse_time("13:37:07"), "Player_YY", "blew up"),
        )

    def test_death_event_alt(self):
        self.assertEqual(
            parse_event("[13:37:07 INFO]: Player_YY was slain by Iron Golem"),
            LogEvent(
                "Death", parse_time("13:37:07"), "Player_YY", "was slain by Iron Golem"
            ),
        )

    def test_game_mode_event(self):
        self.assertEqual(
            parse_event(
                "[13:37:07 INFO]: [Player_YY: Set own game mode to Survival Mode]"
            ),
            LogEvent("GameMode", parse_time("13:37:07"), "Player_YY", "Survival Mode"),
        )

    def test_message_event(self):
        self.assertEqual(
            parse_event("[13:37:07 INFO]: <Player_YY> hey bud"),
            LogEvent("Message", parse_time("13:37:07"), "Player_YY", "hey bud"),
        )


class TestParseTime(unittest.TestCase):
    def test_assumes_log_has_todays_date(self):
        self.assertEqual(
            parse_time("10:11:12").date(),
            datetime.now().date(),
        )


if __name__ == "__main__":
    unittest.main()
