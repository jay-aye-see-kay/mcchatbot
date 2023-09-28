import re
from datetime import datetime

from pydantic.dataclasses import dataclass

from lib.db import BaseEvent

deaths = [
    "blew up",
    "burned to death",
    "didn't want to live in the same world as ",
    "discovered the floor was lava",
    "drowned",
    "experienced kinetic energy",
    "fell from a high place",
    "fell off a ladder",
    "fell off scaffolding",
    "fell off some twisting vines",
    "fell off some vines",
    "fell off some weeping vines",
    "fell out of the world",
    "fell while climbing",
    "froze to death",
    "hit the ground too hard",
    "starved to death",
    "suffocated in a wall",
    "tried to swim in lava",
    "walked into danger zone due to ",
    "was blown up by ",
    "was fireballed by ",
    "was frozen to death by ",
    "was impaled by",
    "was impaled on a stalagmite",
    "was killed by",
    "was killed trying to hurt ",
    "was poked to death by a sweet berry bush",
    "was pricked to death",
    "was pummeled by",
    "was shot by ",
    "was skewered by a falling stalactite",
    "was slain by ",
    "was squashed by ",
    "was squished too much",
    "was struck by lightning",
    "was stung to death",
    "went off with a bang",
    "went up in flames",
    "withered away",
]


def is_death(line: str) -> bool:
    if line.startswith("Villager"):
        return False
    for death in deaths:
        if death in line:
            return True
    return False


@dataclass
class MessageEvent(BaseEvent):
    time: datetime
    username: str
    text: str

    def __str__(self):
        return f'at "{self.time}" {self.username} said "{self.text}"\n'


@dataclass
class JoinEvent(BaseEvent):
    time: datetime
    username: str

    def __str__(self):
        return f'at "{self.time}" {self.username} joined the game\n'


@dataclass
class LeaveEvent(BaseEvent):
    time: datetime
    username: str

    def __str__(self):
        return f'at "{self.time}" {self.username} left the game\n'


@dataclass
class DeathEvent(BaseEvent):
    time: datetime
    username: str
    description: str

    def __str__(self):
        return f'at "{self.time}" {self.username} {self.description} (they died)\n'


@dataclass
class GameModeEvent(BaseEvent):
    time: datetime
    username: str
    game_mode: str

    def __str__(self):
        return (
            f'at "{self.time}" {self.username} '
            f"set their game mode to {self.game_mode}\n"
        )



def parse_time(time_str: str) -> datetime:
    return datetime.strptime(time_str, "%H:%M:%S")


def parse_event(line: str) -> BaseEvent | None:
    match = re.search(
        r"\[(?P<time>\d{2}:\d{2}:\d{2}) INFO\]: (?:<(?P<username>.+?)> )?(?P<text>.*)",
        line,
    )
    line_content = re.sub(r"^\[.*\]: ", "", line)
    game_mode_match = re.search(
        r"\[.*\]: \[(?P<username>.*): Set own game mode to (?P<game_mode>.*)\]", line
    )
    if not match:
        return
    elif match.group("username"):
        return MessageEvent(
            time=parse_time(match.group("time")),
            username=match.group("username"),
            text=match.group("text"),
        )
    elif line.endswith("joined the game"):
        username = re.sub(r" joined the game$", "", line_content)
        return JoinEvent(
            time=parse_time(match.group("time")),
            username=username,
        )
    elif line.endswith("left the game"):
        username = re.sub(r" left the game$", "", line_content)
        return LeaveEvent(
            time=parse_time(match.group("time")),
            username=username,
        )
    elif is_death(line_content):
        words = line_content.split()
        username = words[0]
        description = " ".join(words[1:])
        return DeathEvent(parse_time(match.group("time")), username, description)
    elif game_mode_match:
        return GameModeEvent(
            time=parse_time(match.group("time")),
            username=game_mode_match.group("username"),
            game_mode=game_mode_match.group("game_mode"),
        )
