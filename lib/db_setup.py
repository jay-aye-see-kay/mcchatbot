import sqlite3
from datetime import datetime

from lib.db import BaseEvent
from lib.events import (DeathEvent, GameModeEvent, JoinEvent, LeaveEvent,
                        MessageEvent)

# dummy initialised events required to get create table syntax
dummy_events: list[BaseEvent] = [
    MessageEvent(datetime.now(), "me", "hi"),
    JoinEvent(datetime.now(), "me"),
    LeaveEvent(datetime.now(), "me"),
    DeathEvent(datetime.now(), "me", "drowned"),
    GameModeEvent(datetime.now(), "me", "Survival Mode"),
]


def ensure_db_setup(db: sqlite3.Connection):
    for event in dummy_events:
        db.execute(event.sql_create_table())
    pass
