import unittest
import mcchatbot

class TestIsDeath(unittest.TestCase):
    def test_ignores_villager(self):
        self.assertFalse(mcchatbot.is_death("Villager blew up"))

    def test_ignores_other_logs(self):
        ignorable_logs = [
                "[player_XX: Set own game mode to Spectator Mode]",
                "Thread [RCON](2023-09-24_rcon.md) Client /127.0.0.1 started",
                "Thread RCON Client /127.0.0.1 shutting down",
                "player_XX lost connection: Disconnected",
                "player_XX left the game",
                "UUID of player Player_YY is 548724a6-ae80-41af-9144-f6a02ab27fcb",
                "Player_YY joined the game",
                "Player_YY[/172.19.0.4:60669] logged in with entity id 53844 at ([world]210.27267354636194, 167.5, -97.29571541611286)",
                "Villager EntityVillager['Farmer'/61310, uuid='a0772acd-e86c-44f5-ad3a-b21c26ad0a7e', l='ServerLevel[world]', x=220.30, y=179.00, z=-63.30, cpos=[13, -4], tl=395686, v=true] died, message: 'Farmer was slain by Zombie'",
                ]
        for log in ignorable_logs:
            with self.subTest(log=log):
                self.assertFalse(mcchatbot.is_death(log))

    def test_true_on_death(self):
        self.assertTrue(mcchatbot.is_death("Player_YY blew up"))

if __name__ == '__main__':
    unittest.main()
