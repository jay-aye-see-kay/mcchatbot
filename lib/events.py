import re
from datetime import datetime
from typing import Literal, assert_never

from pydantic.dataclasses import dataclass

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


EventType = (
    Literal["Message"]
    | Literal["Join"]
    | Literal["Leave"]
    | Literal["Death"]
    | Literal["GameMode"]
)


@dataclass
class LogEvent:
    event_type: EventType
    time: datetime
    username: str
    text: str

    def __iter__(self):
        yield self.event_type
        yield self.time
        yield self.username
        yield self.text

    def to_context_line(self):
        time_str = f"{self.time:%H:%M:%S}"
        match self.event_type:
            case "Message":
                return f'at "{time_str}" {self.username} said "{self.text}"\n'
            case "Join":
                return f'at "{time_str}" {self.username} joined the game\n'
            case "Leave":
                return f'at "{time_str}" {self.username} left the game\n'
            case "Death":
                return f'at "{time_str}" {self.username} {self.text} (they died)\n'
            case "GameMode":
                return (
                    f'at "{time_str}" {self.username} '
                    f"set their game mode to {self.text}\n"
                )
            case _:
                assert_never(self.event_type)

    def should_respond(self):
        return self.event_type != "Leave"


def parse_time(time_str: str) -> datetime:
    parsed_time = datetime.strptime(time_str, "%H:%M:%S")
    today = datetime.now()
    return datetime(
        year=today.year,
        month=today.month,
        day=today.day,
        hour=parsed_time.hour,
        minute=parsed_time.minute,
        second=parsed_time.second,
    )


def parse_event(line: str) -> LogEvent | None:
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
        return LogEvent(
            event_type="Message",
            time=parse_time(match.group("time")),
            username=match.group("username"),
            text=match.group("text"),
        )
    elif line.endswith("joined the game"):
        username = re.sub(r" joined the game$", "", line_content)
        return LogEvent(
            event_type="Join",
            time=parse_time(match.group("time")),
            username=username,
            text="",
        )
    elif line.endswith("left the game"):
        username = re.sub(r" left the game$", "", line_content)
        return LogEvent(
            event_type="Leave",
            time=parse_time(match.group("time")),
            username=username,
            text="",
        )
    elif is_death(line_content):
        words = line_content.split()
        username = words[0]
        description = " ".join(words[1:])
        return LogEvent(
            event_type="Death",
            time=parse_time(match.group("time")),
            username=username,
            text=description,
        )
    elif game_mode_match:
        return LogEvent(
            event_type="GameMode",
            time=parse_time(match.group("time")),
            username=game_mode_match.group("username"),
            text=game_mode_match.group("game_mode"),
        )
