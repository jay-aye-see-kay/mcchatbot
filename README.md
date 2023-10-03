# A minecraft chatbot

## What and why

Have you ever wanted a chatbot to say hi when you join or insult you when you die? I did, and it was surprisingly nice to have around so I've made it a container others can use.

![swappy-20231003-210656](https://github.com/jay-aye-see-kay/mcchatbot/assets/23488939/2408e7e0-7718-480a-acbb-19f794e3db3e)

It's pretty hacky, if you find bugs or have improvements let me know.

## Requirements

- requires a minecraft running in a docker container with `rcon-cli` installed
- doesn't requires any minecraft plugins, works by listening to server logs and responding via `rcon-cli`

## Example setup

```yaml
# file: ./docker-compose.yaml
version: "3"
services:
  minecraft_server:
    container_name: your_minecraft_server # important so you have a stable container name
    image: itzg/minecraft-server:java17
    volumes:
      - ./game-data:/data
    environment:
      EULA: "TRUE"
      VERSION: "1.20.1"

  mcchatbot:
    image: jayayeseekay/mcchatbot:0.2
    env_file: ".env" # important to read OPENAI_API_KEY
    environment:
      MCC_CONTAINER_NAME: your_minecraft_server # must match container_name above
      MCC_BOT_NAME: "Wheatly"
      MCC_SYSTEM_MESSAGE: |
        You are the chacter Wheatley from Portal 2.
        Do not offer assistance or try to be helpful. 
        Keep your responses short, about 1 line. 
    volumes:
      - ./mcchatbot-data:/var/lib/mcchatbot
      # required: read-only access to docker to get logs
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

```bash
# file: ./.env
OPENAI_API_KEY="your api key"
```

## Configuration options

All config is done by environment variables. Documentation is best effort, see ./lib/config.py for source of truth.

- `MCC_CONTAINER_NAME`: **required**, the container name of the minecraft server
- `MCC_BOT_NAME`: (default: "Wheatly") the name the bot show's up as, will only refer to itself by this name if you tell it to in the system message
- `MCC_SYSTEM_MESSAGE`: text describing the bot's character and behaviour
- `MCC_CONTEXT_MESSAGE_LIMIT`: (default 30) number of events and chat messages to send to the ai model
  - more increases cost per request
  - less reduces the "memory" of the bot, meaning it won't consider older messages in conversation
- `MCC_REPLACE_NAMES`: allows replacing usernames before sending chat to ai model
  - useful if you want the bot to talk to you by name, rather than username
  - for example if John's username was `elder_john_69`, and Jane's was `tank_girl_89` the following setting would make the ai use their names: `MCC_REPLACE_NAMES: "elder_john_69=John, tank_girl_89=Jane"`
  - note this setting replaces username with names, so the ai can no longer see the original usernames
- `MCC_OPENAI_MODEL`: https://platform.openai.com/docs/api-reference/chat/create#model
- `MCC_TEMPERATURE`: https://platform.openai.com/docs/api-reference/chat/create#temperature
- `MCC_PRESENCE_PENALTY`: https://platform.openai.com/docs/api-reference/chat/create#presence_penalty
- `MCC_FREQUENCY_PENALTY`: https://platform.openai.com/docs/api-reference/chat/create#frequency_penalty
- `MCC_MAX_TOKENS`: https://platform.openai.com/docs/api-reference/chat/create#max_tokens

## Roadmap / todo / ideas

- [x] update github action to push a "latest" tag image
- [x] arm64 version of image
- [ ] add "personas" and more customisation of the system prompt
- [ ] support for multiple personas (still one response per event, but pick a persona at random each time)
- [ ] rotate logs from database (currently keeps logs forever)
- [ ] log api use by token in database (to approximate cost)
- [ ] support other models/providers
