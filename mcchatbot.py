#!/usr/bin/env python

# run like:
#     export OPENAI_API_KEY="..."; ./chatbot.py

import re
import subprocess
from datetime import datetime, timedelta
from time import sleep

import openai

from lib.config import Config
from lib.events import LeaveEvent, LogEvent, MessageEvent, parse_event


def now_str() -> str:
    return datetime.strftime(datetime.now(), "%H:%M:%S")


def should_respond(event: LogEvent):
    if isinstance(event, LeaveEvent):
        return False
    return True


init_time = datetime.now()

all_messages: list[LogEvent] = []


def respond_to_event(cfg: Config, event: LogEvent):
    # store all old logs in memory
    all_messages.append(event)

    # ignore first 5 sec of logs as we're probably loading up old ones
    if not init_time + timedelta(seconds=5) < datetime.now():
        return
    chat_msg = "Here is a list of previous logs and messages in the conversation:\n"

    # limit to message count in logs
    first_idx = 0
    if len(all_messages) < cfg.context_message_limit:
        first_idx = len(all_messages) - cfg.context_message_limit

    for msg in all_messages[first_idx:]:
        chat_msg += msg.to_s()
    if not should_respond(event):
        return
    # get response
    completion = openai.ChatCompletion.create(
        model=cfg.openai_model,
        messages=[
            {"role": "system", "content": cfg.system_message},
            {"role": "user", "content": chat_msg},
        ],
    )
    response = completion.choices[0].message.content  # type: ignore
    # remove invalid characters
    response = re.sub(r"\n", " ", response)
    response = re.sub(r'"', "", response)
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


def listen_to_events(cfg: Config):
    process = subprocess.Popen(
        ["docker", "logs", "-f", cfg.container_name],
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    try:
        for line in iter(process.stdout.readline, ""):  # type: ignore
            event = parse_event(line.strip())
            if event:
                respond_to_event(cfg, event)
    except KeyboardInterrupt:
        process.terminate()


def listen_or_retry(cfg: Config):
    while True:
        listen_to_events(cfg)
        print(
            f"Could not connect to {cfg.container_name}, "
            f"trying again in {cfg.retry_delay_seconds} seconds..."
        )
        sleep(cfg.retry_delay_seconds)


if __name__ == "__main__":
    cfg = Config()
    listen_or_retry(cfg)
