
# Hexa Anime v2.0

Ready-to-deploy Telegram bot (Hexa Anime v2.0).

## What is included
- `bot.py` : Main bot code (uses AniList, waifu.pics, animechan APIs)
- `requirements.txt` : Python dependencies
- `watchlists.json`, `guess_state.json` : will be created at runtime (not included)

## Quick deploy (Render)
1. Push this repo to GitHub.
2. Create a new **Web Service** on Render and connect your repo.
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
3. In Render dashboard -> Environment -> Add Variable:
   - Key: `BOT_TOKEN`
   - Value: `<your telegram bot token>`
4. Deploy. Bot will start and run 24/7 on Render.

## Notes
- Do NOT commit your bot token into the repo.
- AniList GraphQL used for anime and character info (no API key needed).
- Some endpoints are free public APIs and may rate-limit; upgrade later if needed.

## Local testing
- Create a file `watchlists.json` with `{}` and `guess_state.json` with `{}` or let the bot create them.
- Set environment variable `BOT_TOKEN` locally and run:
  ```
  python -m pip install -r requirements.txt
  python bot.py
  ```

