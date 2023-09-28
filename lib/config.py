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
    def __init__(self):
        self.container_name = os.environ["CONTAINER_NAME"]
        # container_name = os.environ.get("CONTAINER_NAME")
        self.retry_delay_seconds = int(os.environ.get("RETRY_DELAY_SECONDS", 30))
        self.openai_model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        self.system_message = system_message
        self.persona = "Wheatley"
        self.context_message_limit = int(os.environ.get("CONTEXT_MESSAGE_LIMIT", 30))
