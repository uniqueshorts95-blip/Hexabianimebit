
# Hexa Anime v2.0 - Replit/Render-ready
# Requirements: python-telegram-bot==13.17, requests
# NOTE: Do NOT put your BOT token in this file. Use environment variable BOT_TOKEN on Render / Secrets on Replit.

import os
import json
import random
import requests
from telegram import Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext

# ----------------------
# Config & storage
# ----------------------
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set. Add it as a Replit Secret or Render environment variable.")

WATCHLIST_FILE = "watchlists.json"
GUESS_FILE = "guess_state.json"

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# initialize files
watchlists = load_json(WATCHLIST_FILE, {})
guess_state = load_json(GUESS_FILE, {})

# ----------------------
# Helpers: AniList GraphQL
# ----------------------
ANILIST_URL = "https://graphql.anilist.co"

def anilist_search_media(name):
    query = '''
    query ($search: String) {
      Media(search: $search, type: ANIME) {
        id
        title { romaji english native }
        episodes
        status
        averageScore
        description(asHtml: false)
        genres
        coverImage { large medium }
        siteUrl
      }
    }
    '''
    try:
        resp = requests.post(ANILIST_URL, json={"query": query, "variables": {"search": name}}, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("data", {}).get("Media")
    except Exception as e:
        print("AniList error:", e)
    return None

def anilist_search_character(name):
    query = '''
    query ($search: String) {
      Character(search: $search) {
        id
        name { full native }
        age
        gender
        description(asHtml: false)
        image { large medium }
        siteUrl
      }
    }
    '''
    try:
        resp = requests.post(ANILIST_URL, json={"query": query, "variables": {"search": name}}, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("data", {}).get("Character")
    except Exception as e:
        print("AniList char error:", e)
    return None

# ----------------------
# Command handlers
# ----------------------
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "✨ Welcome to *Hexa Anime*! ✨\n\n"
        "Type /help to see all commands. Example: /anime Naruto\n\n"
        "Quick commands: /randomanime /trending /waifu /quote /guessanime",
        parse_mode="Markdown"
    )

def help_cmd(update: Update, context: CallbackContext):
    msg = (
        "*Hexa Anime - Commands*\n\n"
        "/anime <name> - Search anime info\n"
        "/character <name> - Search character info\n"
        "/randomanime - Random anime suggestion\n"
        "/trending - Trending anime (sample)\n"
        "/upcoming - Upcoming anime (sample)\n"
        "/airing - Currently airing (sample)\n"
        "/animegif - Random anime GIF link\n"
        "/waifu - Random waifu image\n"
        "/husbando - Random husbando image\n"
        "/wallpaper - Random anime wallpaper\n"
        "/quote - Random anime quote\n"
        "/quotechar <name> - Quote by character\n"
        "/animefact - Random anime fact\n"
        "/guessanime - Start guess-the-anime game\n"
        "/op - Anime opening info (placeholder)\n"
        "/ed - Anime ending info (placeholder)\n"
        "/schedule - Today's schedule (placeholder)\n"
        "/addwatch <name> - Add anime to your watchlist\n"
        "/watchlist - View your watchlist\n"
        "/removewatch <name> - Remove from watchlist\n"
        "/about - About this bot\n"
        "/ping - Check bot status\n"
    )
    update.message.reply_text(msg, parse_mode="Markdown")

def ping(update: Update, context: CallbackContext):
    update.message.reply_text("🏓 Pong! Hexa Anime is online.")

def about(update: Update, context: CallbackContext):
    update.message.reply_text("Hexa Anime v2.0 — Made for anime lovers. Bot provides quick info and fun utilities.")

# ---- /anime <name>
def anime_cmd(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("🔍 Use: /anime <anime name>\nExample: /anime Naruto")
        return
    name = " ".join(context.args)
    update.message.reply_text(f"🔎 Searching AniList for *{name}* ...", parse_mode="Markdown")
    data = anilist_search_media(name)
    if not data:
        update.message.reply_text("❌ No results found or AniList error.")
        return

    title = data["title"].get("english") or data["title"].get("romaji") or data["title"].get("native")
    episodes = data.get("episodes", "Unknown")
    score = data.get("averageScore", "N/A")
    status = data.get("status", "Unknown")
    genres = ", ".join(data.get("genres", [])) or "N/A"
    desc = data.get("description") or "No description."
    site = data.get("siteUrl", "")
    cover = data.get("coverImage", {}).get("large")

    text = f"*{title}*\nEpisodes: `{episodes}`  |  Score: `{score}`\nStatus: `{status}`\nGenres: {genres}\n\n"
    text += (desc[:600] + ("..." if len(desc) > 600 else "")) + f"\n\nMore: {site}"
    try:
        if cover:
            update.message.reply_photo(photo=cover, caption=text, parse_mode="Markdown")
        else:
            update.message.reply_text(text, parse_mode="Markdown")
    except Exception:
        update.message.reply_text(text, parse_mode="Markdown")

# ---- /character <name>
def character_cmd(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("👤 Use: /character <name>\nExample: /character Naruto Uzumaki")
        return
    name = " ".join(context.args)
    update.message.reply_text(f"🔎 Searching AniList for character *{name}* ...", parse_mode="Markdown")
    data = anilist_search_character(name)
    if not data:
        update.message.reply_text("❌ Character not found or AniList error.")
        return

    fullname = data.get("name", {}).get("full") or "Unknown"
    age = data.get("age") or "Unknown"
    gender = data.get("gender") or "Unknown"
    desc = data.get("description") or "No description."
    img = data.get("image", {}).get("large")
    site = data.get("siteUrl", "")

    text = f"*{fullname}*\nAge: `{age}`  |  Gender: `{gender}`\n\n" + (desc[:600] + ("..." if len(desc) > 600 else "")) + f"\n\nMore: {site}"
    try:
        if img:
            update.message.reply_photo(photo=img, caption=text, parse_mode="Markdown")
        else:
            update.message.reply_text(text, parse_mode="Markdown")
    except Exception:
        update.message.reply_text(text, parse_mode="Markdown")

# ---- Random / Trending / Upcoming / Airing (simple)
def randomanime(update: Update, context: CallbackContext):
    sample = ["Naruto", "One Piece", "Jujutsu Kaisen", "Demon Slayer", "Spy x Family", "Attack on Titan", "My Hero Academia"]
    pick = random.choice(sample)
    update.message.reply_text(f"🎲 Random suggestion: *{pick}*", parse_mode="Markdown")

def trending_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("🔥 Trending this week:\n1. Attack on Titan\n2. Demon Slayer\n3. Jujutsu Kaisen\n4. One Piece", parse_mode="Markdown")

def upcoming_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("📅 Upcoming releases (sample):\n- Chainsaw Man S2\n- Solo Leveling\n- New OVA releases", parse_mode="Markdown")

def airing_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("📺 Currently airing (sample):\n- One Piece\n- Jujutsu Kaisen\n- Spy x Family", parse_mode="Markdown")

# ---- Images: animegif, waifu, husbando, wallpaper
def animegif_cmd(update: Update, context: CallbackContext):
    try:
        res = requests.get("https://api.waifu.pics/sfw/megumin", timeout=8)
        if res.ok:
            url = res.json().get("url")
            update.message.reply_text(f"🎬 Anime GIF: {url}")
            return
    except:
        pass
    update.message.reply_text("Couldn't fetch GIF. Try again later.")

def waifu_cmd(update: Update, context: CallbackContext):
    try:
        res = requests.get("https://api.waifu.pics/sfw/waifu", timeout=8)
        if res.ok:
            update.message.reply_photo(photo=res.json().get("url"))
            return
    except:
        pass
    update.message.reply_text("Couldn't fetch waifu image now.")

def husbando_cmd(update: Update, context: CallbackContext):
    try:
        res = requests.get("https://api.waifu.pics/sfw/megumin", timeout=8)
        if res.ok:
            update.message.reply_photo(photo=res.json().get("url"))
            return
    except:
        pass
    update.message.reply_text("Couldn't fetch husbando image now.")

def wallpaper_cmd(update: Update, context: CallbackContext):
    try:
        res = requests.get("https://api.waifu.pics/sfw/wallpaper", timeout=8)
        if res.ok:
            update.message.reply_photo(photo=res.json().get("url"))
            return
    except:
        pass
    update.message.reply_text("Couldn't fetch wallpaper now.")

# ---- Quotes: animechan
def quote_cmd(update: Update, context: CallbackContext):
    try:
        res = requests.get("https://animechan.vercel.app/api/random", timeout=8)
        if res.ok:
            j = res.json()
            update.message.reply_text(f"💬 \"{j.get('quote')}\"\n— *{j.get('character')}* from _{j.get('anime')}_", parse_mode="Markdown")
            return
    except:
        pass
    update.message.reply_text("Couldn't fetch quote right now.")

def quotechar_cmd(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Use: /quotechar <character name>\nExample: /quotechar Naruto")
        return
    name = " ".join(context.args)
    try:
        res = requests.get(f"https://animechan.vercel.app/api/quotes/character?name={requests.utils.requote_uri(name)}", timeout=8)
        if res.ok:
            arr = res.json()
            if isinstance(arr, list) and arr:
                pick = random.choice(arr)
                update.message.reply_text(f"💬 \"{pick.get('quote')}\"\n— *{pick.get('character')}* from _{pick.get('anime')}_", parse_mode="Markdown")
                return
    except:
        pass
    update.message.reply_text("No quotes found for that character.")

# ---- animefact (simple static facts)
FACTS = [
    "The first anime was made in 1917 (short animations).",
    "Astro Boy (1963) is considered the first popular TV anime.",
    "Studio Ghibli was co-founded by Hayao Miyazaki.",
]
def animefact_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("📘 Anime Fact: " + random.choice(FACTS))

# ---- guessanime game
def guessanime_cmd(update: Update, context: CallbackContext):
    sample = ["Naruto", "One Piece", "Death Note", "Demon Slayer", "Attack on Titan", "Fullmetal Alchemist"]
    pick = random.choice(sample)
    user = str(update.effective_user.id)
    guess_state[user] = {"answer": pick.lower(), "tries": 0}
    save_json(GUESS_FILE, guess_state)
    update.message.reply_text("🎮 Guess the Anime! I'll give a hint: It's popular. Type your guess in chat (just send the name).")

def handle_text(update: Update, context: CallbackContext):
    user = str(update.effective_user.id)
    text = update.message.text.strip()
    if user in guess_state:
        state = guess_state[user]
        state["tries"] += 1
        if text.lower() == state["answer"]:
            update.message.reply_text(f"✅ Correct! The anime was *{state['answer'].title()}* (tries: {state['tries']})", parse_mode="Markdown")
            del guess_state[user]
            save_json(GUESS_FILE, guess_state)
        else:
            update.message.reply_text("❌ Wrong guess. Try again or type /giveup to stop.")
            guess_state[user] = state
            save_json(GUESS_FILE, guess_state)
        return
    return

def giveup_cmd(update: Update, context: CallbackContext):
    user = str(update.effective_user.id)
    if user in guess_state:
        ans = guess_state[user]["answer"]
        del guess_state[user]
        save_json(GUESS_FILE, guess_state)
        update.message.reply_text(f"Game ended. Answer was *{ans.title()}*.", parse_mode="Markdown")
    else:
        update.message.reply_text("You're not in a guess game. Start one with /guessanime.")

# ---- watchlist: addwatch, watchlist, removewatch
def addwatch_cmd(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Use: /addwatch <anime name>")
        return
    user = str(update.effective_user.id)
    name = " ".join(context.args)
    user_list = watchlists.get(user, [])
    if name in user_list:
        update.message.reply_text("This anime is already in your watchlist.")
        return
    user_list.append(name)
    watchlists[user] = user_list
    save_json(WATCHLIST_FILE, watchlists)
    update.message.reply_text(f"✅ Added *{name}* to your watchlist.", parse_mode="Markdown")

def watchlist_cmd(update: Update, context: CallbackContext):
    user = str(update.effective_user.id)
    user_list = watchlists.get(user, [])
    if not user_list:
        update.message.reply_text("Your watchlist is empty. Add with /addwatch <name>.")
        return
    text = "📜 Your Watchlist:\n" + "\n".join(f"- {x}" for x in user_list)
    update.message.reply_text(text)

def removewatch_cmd(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Use: /removewatch <anime name>")
        return
    user = str(update.effective_user.id)
    name = " ".join(context.args)
    user_list = watchlists.get(user, [])
    if name not in user_list:
        update.message.reply_text("That anime isn't in your watchlist.")
        return
    user_list.remove(name)
    watchlists[user] = user_list
    save_json(WATCHLIST_FILE, watchlists)
    update.message.reply_text(f"❌ Removed *{name}* from your watchlist.", parse_mode="Markdown")

# ---- placeholders for op/ed/schedule
def op_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("🎵 OP info feature coming soon. Use /anime <name> to get anime details.")

def ed_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("🎵 ED info feature coming soon. Use /anime <name> to get anime details.")

def schedule_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("📅 Schedule feature coming soon. Use /airing for quick current shows.")

# ----------------------
# Main setup
# ----------------------
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("anime", anime_cmd))
    dp.add_handler(CommandHandler("character", character_cmd))
    dp.add_handler(CommandHandler("randomanime", randomanime))
    dp.add_handler(CommandHandler("trending", trending_cmd))
    dp.add_handler(CommandHandler("upcoming", upcoming_cmd))
    dp.add_handler(CommandHandler("airing", airing_cmd))
    dp.add_handler(CommandHandler("animegif", animegif_cmd))
    dp.add_handler(CommandHandler("waifu", waifu_cmd))
    dp.add_handler(CommandHandler("husbando", husbando_cmd))
    dp.add_handler(CommandHandler("wallpaper", wallpaper_cmd))
    dp.add_handler(CommandHandler("quote", quote_cmd))
    dp.add_handler(CommandHandler("quotechar", quotechar_cmd))
    dp.add_handler(CommandHandler("animefact", animefact_cmd))
    dp.add_handler(CommandHandler("guessanime", guessanime_cmd))
    dp.add_handler(CommandHandler("giveup", giveup_cmd))
    dp.add_handler(CommandHandler("addwatch", addwatch_cmd))
    dp.add_handler(CommandHandler("watchlist", watchlist_cmd))
    dp.add_handler(CommandHandler("removewatch", removewatch_cmd))
    dp.add_handler(CommandHandler("op", op_cmd))
    dp.add_handler(CommandHandler("ed", ed_cmd))
    dp.add_handler(CommandHandler("schedule", schedule_cmd))

    # Text handler (for guess game)
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    print("Hexa Anime bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
