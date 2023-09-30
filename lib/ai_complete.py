import logging
import re
from datetime import datetime
from typing import Callable

import openai

from lib.config import Config
from lib.events import LogEvent

AiComplete = Callable[[Config, str], str]


def openai_complete(cfg: Config, content: str) -> str:
    completion = openai.ChatCompletion.create(
        model=cfg.openai_model,
        temperature=cfg.temperature,
        presence_penalty=cfg.presence_penalty,
        frequency_penalty=cfg.frequency_penalty,
        max_tokens=cfg.max_tokens,
        messages=[
            {"role": "system", "content": cfg.system_message},
            {"role": "user", "content": content},
        ],
    )
    logging.info(f"openai usage: {completion.usage}")  # type: ignore
    return completion.choices[0].message.content  # type: ignore


def sanitize_message(msg: str) -> str:
    msg = re.sub(r"\n", " ", msg)  # can't have newlines in a message
    msg = re.sub(r'"', "", msg)  # quotes seem to mess things up too
    return msg


def format_ai_message(cfg: Config, messages: list[LogEvent]):
    chat_msg = "Here is a list of previous logs and messages in the conversation:\n"
    for msg in messages:
        chat_msg += msg.to_context_line(cfg)
    return chat_msg


def get_response(
    cfg: Config, context_messages: list[LogEvent], ai_complete: AiComplete
) -> LogEvent:
    prompt = format_ai_message(cfg, context_messages)
    logging.debug(f"sending prompt: {prompt}")

    response = ai_complete(cfg, prompt)
    logging.info(f"received response: {response}")

    return LogEvent(
        "Message",
        datetime.now(),
        cfg.persona,
        sanitize_message(response),
    )
