#!/usr/bin/env python

# run like:
#     export OPENAI_API_KEY="..."; ./chatbot.py

import re
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta

import openai

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


class LogEvent(ABC):
    @abstractmethod
    def to_s(self):
        return ""


@dataclass
class MessageEvent(LogEvent):
    time: str
    username: str
    text: str = ""

    def to_s(self):
        return f'at "{self.time}" {self.username} said "{self.text}"\n'


@dataclass
class JoinEvent(LogEvent):
    time: str
    username: str

    def to_s(self):
        return f'at "{self.time}" {self.username} joined the game\n'


@dataclass
class LeaveEvent(LogEvent):
    time: str
    username: str

    def to_s(self):
        return f'at "{self.time}" {self.username} left the game\n'


@dataclass
class DeathEvent(LogEvent):
    time: str
    text: str = ""

    def to_s(self):
        return f'at "{self.time}" {self.text} (they died)\n'


@dataclass
class GameModeEvent(LogEvent):
    time: str
    username: str
    game_mode: str = ""

    def to_s(self):
        return (
            f'at "{self.time}" {self.username} '
            f"set their game mode to {self.game_mode}\n"
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
        return MessageEvent(
            time=match.group("time"),
            username=match.group("username"),
            text=match.group("text"),
        )
    elif line.endswith("joined the game"):
        username = re.sub(r" joined the game$", "", line_content)
        return JoinEvent(
            time=match.group("time"),
            username=username,
        )
    elif line.endswith("left the game"):
        username = re.sub(r" left the game$", "", line_content)
        return LeaveEvent(
            time=match.group("time"),
            username=username,
        )
    elif is_death(line_content):
        text = re.sub(r"^\[.*\]: ", "", line)
        return DeathEvent(time=match.group("time"), text=text)
    elif game_mode_match:
        return GameModeEvent(
            time=match.group("time"),
            username=game_mode_match.group("username"),
            game_mode=game_mode_match.group("game_mode"),
        )


def now_str() -> str:
    return datetime.strftime(datetime.now(), "%H:%M:%S")


def should_respond(event: LogEvent):
    if isinstance(event, LeaveEvent):
        return False
    return True


init_time = datetime.now()

system_message = """
    You are the chacter Wheatley from Portal 2 chatting with people playing minecraft.
    Your responses must be formatted in plain text only. 
    Previous messages include a timestamp and username only for your context, you 
    must not include these in your responses. 
    After someone leaves the game they cannot see what you say, but remaining players 
    can. Do not offer assistance or try to be helpful. 
    Keep your responses relatively short, about 1 line. 
    If there is nothing to say in the coversation make a joke or insult someone."""

CONTEXT_MSGS = 30
all_messages: list[LogEvent] = []


def respond_to_event(event: LogEvent):
    # store all old logs in memory
    all_messages.append(event)
    # ignore first 5 sec of logs as we're probably loading up old ones
    if not init_time + timedelta(seconds=5) < datetime.now():
        return
    chat_msg = "Here is a list of previous logs and messages in the conversation:\n"
    # limit to CONTEXT_MSGS most recent logs
    first_idx = (
        0 if len(all_messages) < CONTEXT_MSGS else len(all_messages) - CONTEXT_MSGS
    )
    for msg in all_messages[first_idx:]:
        chat_msg += msg.to_s()
    print(f"DEBUGPRINT[2]: chat_msg={chat_msg}")
    if not should_respond(event):
        return
    # get response
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": chat_msg},
        ],
    )
    response = completion.choices[0].message.content  # type: ignore
    # remove invalid characters
    response = re.sub(r"\n", " ", response)
    response = re.sub(r'"', "", response)
    print(f"DEBUGPRINT[1]: response={response}")
    # save this message (it won't be in the logs)
    all_messages.append(MessageEvent(now_str(), "Wheatley", response))
    process_cmd = [
        "docker-compose",
        "exec",
        "business",
        "rcon-cli",
        "tellraw",
        "@a",
        f'"<Wheatley> {response}"',
    ]
    subprocess.run(process_cmd)


def listen_to_events():
    process = subprocess.Popen(
        ["docker", "logs", "-f", "mc_business"],
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    try:
        for line in iter(process.stdout.readline, ""):  # type: ignore
            event = parse_event(line.strip())
            if event:
                respond_to_event(event)
    except KeyboardInterrupt:
        process.terminate()


if __name__ == "__main__":
    listen_to_events()
