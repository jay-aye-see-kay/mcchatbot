#!/usr/bin/env python

# run like:
#     export OPENAI_API_KEY="..."; ./chatbot.py

import sqlite3
import subprocess
from time import sleep

from lib.ai_complete import get_response, openai_complete
from lib.config import Config
from lib.db import ensure_db_setup, init_db, query_context_messages, save_event
from lib.events import LogEvent, parse_event


def say_response(cfg: Config, msg: LogEvent):
    cmd = [
        "docker",
        "exec",
        cfg.container_name,
        "rcon-cli",
        "tellraw",
        "@a",
        f'"<{msg.username}> {msg.text}"',
    ]
    subprocess.run(cmd)


def handle_event(cfg: Config, db: sqlite3.Connection, event: LogEvent):
    save_event(db, event)
    if not event.should_respond():
        return
    context_messages = query_context_messages(cfg, db)
    response_msg = get_response(cfg, context_messages, openai_complete)
    say_response(cfg, response_msg)
    save_event(db, response_msg)


def listen_to_events(cfg: Config, db: sqlite3.Connection):
    process = subprocess.Popen(
        ["docker", "logs", "--follow", cfg.container_name, "--since", "0m"],
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    try:
        for line in iter(process.stdout.readline, ""):  # type: ignore
            event = parse_event(line.strip())
            if event:
                handle_event(cfg, db, event)
    except KeyboardInterrupt:
        process.terminate()


def main_loop():
    cfg = Config()
    db = init_db(cfg)
    ensure_db_setup(db)
    while True:
        listen_to_events(cfg, db)
        print(
            f"Could not connect to {cfg.container_name}, "
            f"trying again in {cfg.retry_delay_seconds} seconds..."
        )
        sleep(cfg.retry_delay_seconds)


if __name__ == "__main__":
    main_loop()
