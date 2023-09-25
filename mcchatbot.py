#!/usr/bin/env python

# run like:
#     export OPENAI_API_KEY="..."; ./chatbot.py

import re
import subprocess
from datetime import datetime, timedelta

import openai

from lib.events import LeaveEvent, LogEvent, MessageEvent, parse_event


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
