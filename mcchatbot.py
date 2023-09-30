#!/usr/bin/env python

import logging
import sqlite3
from time import sleep

import docker

from lib.ai_complete import get_response, openai_complete
from lib.config import Config
from lib.db import init_db, query_context_messages, save_event
from lib.events import LogEvent, parse_event


def say_response(cfg: Config, msg: LogEvent):
    container = docker.from_env().containers.get(cfg.container_name)
    cmd = ["rcon-cli", "tellraw", "@a", f'"<{msg.username}> {msg.text}"']
    container.exec_run(cmd) # type: ignore


def handle_event(cfg: Config, db: sqlite3.Connection, event: LogEvent):
    save_event(db, event)
    if not event.should_respond():
        logging.info(f"received and ignoring: {event}")
        return
    logging.info(f"received and proceeding: {event}")

    context_messages = query_context_messages(cfg, db)
    logging.debug(f"including {len(context_messages)} context messages")

    response = get_response(cfg, context_messages, openai_complete)
    say_response(cfg, response)
    save_event(db, response)


def listen_to_events(cfg: Config, db: sqlite3.Connection):
    try:
        container = docker.from_env().containers.get(cfg.container_name)
        for line in container.logs(stream=True): # type: ignore
            logging.debug(f"received log line: {line}")
            event = parse_event(line.strip())
            if event:
                handle_event(cfg, db, event)
    except Exception as e:
        logging.debug(f"exception reading from container logs: {e}")
        return


def main_loop():
    cfg = Config()
    logging.basicConfig(encoding="utf-8", level=cfg.log_level)
    db = init_db(cfg)
    while True:
        listen_to_events(cfg, db)
        logging.info(
            f"could not connect to {cfg.container_name}, "
            f"trying again in {cfg.retry_delay_seconds} seconds..."
        )
        sleep(cfg.retry_delay_seconds)


if __name__ == "__main__":
    main_loop()
