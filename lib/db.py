import logging
import sqlite3

from lib.config import Config
from lib.events import LogEvent


def init_db(cfg: Config) -> sqlite3.Connection:
    logging.info(f"opening sqlite file: {cfg.db_path}")
    con = sqlite3.connect(cfg.db_path)
    con.row_factory = sqlite3.Row
    return con


def ensure_db_setup(db: sqlite3.Connection):
    logging.debug('ensuring db table "events" exists')
    db.execute("CREATE TABLE IF NOT EXISTS events(event_type, time, username, text)")


def save_event(db: sqlite3.Connection, event: LogEvent):
    logging.debug(f"inserting {tuple(event)} into events")
    db.execute("INSERT INTO events VALUES (?, ?, ?, ?)", tuple(event))
    db.commit()


def query_context_messages(cfg: Config, db: sqlite3.Connection):
    result = db.execute(
        "SELECT * FROM events"
        " ORDER BY time desc"
        f" LIMIT {cfg.context_message_limit}"
    )
    messages: list[LogEvent] = []
    for row in result:
        messages.append(LogEvent(*row))
    messages.reverse()
    return messages
