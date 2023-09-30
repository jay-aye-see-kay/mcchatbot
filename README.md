# A minecraft chatbot

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

## Roadmap / todo

- [ ] rotate logs from database (currently keeps logs forever)
- [ ] log api use by token in database
- [ ] allow limiting input by tokens
- [ ] support other models/providers
