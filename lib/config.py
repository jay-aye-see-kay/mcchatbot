import logging
import os
import re

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
    replace_names: dict[str, str]
    temperature: float
    presence_penalty: float
    frequency_penalty: float
    max_tokens: int | None

    def __init__(self, **test: bool | None):
        self.system_message = system_message
        self.persona = "Wheatley"
        self.base_path = os.environ.get("MCC_BASE_PATH", "/var/lib/mcchatbot")
        self.replace_names = self.parse_replace_names(
            os.environ.get("MCC_REPLACE_NAMES", "")
        )

        # @see: https://platform.openai.com/docs/api-reference/chat/create?lang=python
        # between 0 and 2, default 1
        self.temperature = float(os.environ.get("MCC_TEMPERATURE", 1))
        # between -2 and 2, default 0
        self.presence_penalty = float(os.environ.get("MCC_PRESENCE_PENALTY", 0))
        # between -2 and 2, default 0
        self.frequency_penalty = float(os.environ.get("MCC_FREQUENCY_PENALTY", 0))
        # default is model's max value
        self.max_tokens = int(os.environ.get("MCC_MAX_TOKENS", 0)) or None

        if test:
            self.container_name = "test"
            self.retry_delay_seconds = 30
            self.openai_model = "gpt-3.5-turbo"
            self.context_message_limit = 30
            self.db_path = ":memory:"
            self.log_level = logging.DEBUG
        else:
            self.container_name = os.environ["MCC_CONTAINER_NAME"]
            self.retry_delay_seconds = int(
                os.environ.get("MCC_RETRY_DELAY_SECONDS", 30)
            )
            self.openai_model = os.environ.get("MCC_OPENAI_MODEL", "gpt-3.5-turbo")
            self.context_message_limit = int(
                os.environ.get("MCC_CONTEXT_MESSAGE_LIMIT", 30)
            )
            self.db_path = os.path.join(self.base_path, "data.sqlite")

            env_debug = os.environ.get("DEBUG")
            if env_debug and env_debug.lower() == "true" or env_debug == "1":
                self.log_level = logging.DEBUG
            else:
                self.log_level = logging.INFO

    def parse_replace_names(self, env_value: str) -> dict[str, str]:
        try:
            parsed = {}
            env_value = re.sub(r" ", "", env_value)
            pairs = env_value.split(",")
            for pair in pairs:
                if "=" in pair:
                    [username, name] = pair.split("=")
                    parsed[username] = name
            return parsed
        except Exception as e:
            logging.error(f"could not parse value of MCC_REPLACE_NAMES {e}")
            return {}


test_config = Config(test=True)
