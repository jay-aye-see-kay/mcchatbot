import logging
import os

system_message = """
    You are the chacter Wheatley from Portal 2 chatting with people playing minecraft.
    Your responses must be formatted in plain text only. 
    Previous messages include a timestamp and username only for your context, you 
    must not include these in your responses. 
    After someone leaves the game they cannot see what you say, but remaining players 
    can. Do not offer assistance or try to be helpful. 
    Keep your responses relatively short, about 1 line. 
    If there is nothing to say in the coversation make a joke or insult someone."""


class Config:
    container_name: str
    retry_delay_seconds: int
    openai_model: str
    system_message: str
    persona: str
    context_message_limit: int
    db_path: str
    log_level: int

    def __init__(self, **test: bool | None):
        self.system_message = system_message
        self.persona = "Wheatley"
        if test:
            self.container_name = "test"
            self.retry_delay_seconds = 30
            self.openai_model = "gpt-3.5-turbo"
            self.context_message_limit = 30
            self.db_path = ":memory:"
            self.log_level = logging.DEBUG
        else:
            self.container_name = os.environ["CONTAINER_NAME"]
            self.retry_delay_seconds = int(os.environ.get("RETRY_DELAY_SECONDS", 30))
            self.openai_model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
            self.context_message_limit = int(
                os.environ.get("CONTEXT_MESSAGE_LIMIT", 30)
            )
            self.db_path = "./events.sqlite"

            env_debug = os.environ.get("DEBUG")
            if env_debug and env_debug.lower() == "true" or env_debug == "1":
                self.log_level = logging.DEBUG
            else:
                self.log_level = logging.INFO


testConfig = Config(test=True)
