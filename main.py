import random
import time
import asyncio
import os
from telethon import TelegramClient, events, tl
from dotenv import load_dotenv

load_dotenv()

# API credentials from Telegram
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
# Initialize the client
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

user_emojis = {}

last_command_times = {}

# List of emojis to assign
emojis = ["😇", "🥰", "😋", "🤨", "🤓", "😔", "🥵", "😥", "🙄", "😮‍💨", "😈", "💩", "🤡", "💀", "🤙", "🫦", "🫀", "🧔🏼‍♀️", "🧑🏽‍⚖️",
          "🫃🏽", "🧏", "💅", "👩🏽‍🦽", "👙", "🐷", "🦁", "🐯", "🦋", "🪰", "🦐", "🦧", "🦍", "🦃", "🍀", "🐾", "🥀", "✨", "🍔", "🍟", "🥃",
          "⚽️", "🤼‍♂️", "🏆", "🪦", "💟", "♠️", "♣️", "♥️", "♦️", "🏳️‍🌈"]

excluded_users = set()

COOLDOWN_DURATION = 60


def get_or_assign_emoji(user_id, emojis, user_emojis):
    emoji = user_emojis.get(user_id)
    if not emoji:
        emoji = random.choice(emojis)
        user_emojis[user_id] = emoji
    return emoji


def is_on_group_cooldown(chat_id):
    cd = COOLDOWN_DURATION
    last_time = last_command_times.get(chat_id, 0)
    return time.time() - last_time < cd


@client.on(events.NewMessage(pattern=r'(?i)^калл(?:\s+(.+))?$'))
async def call_all(event):
    if event.is_group:

        if is_on_group_cooldown(event.chat_id):
            await event.respond(
                "Команда используется слишком часто в этом чате. Подождите 60 секунд перед повторной попыткой.")
            return

        last_command_times[event.chat_id] = time.time()

        # Extract additional message (if provided)
        extra_message = event.pattern_match.group(1)
        if not extra_message:
            extra_message = ""

        participants = await client.get_participants(event.chat_id, filter=tl.types.ChannelParticipantsSearch(''))
        mentions = []

        for user in participants:
            if not user.bot and user.id not in excluded_users:  # Skip bots
                emoji = get_or_assign_emoji(user.id, emojis, user_emojis)
                mentions.append(f"[{emoji}{user.first_name}](tg://user?id={user.id})")

        # Create a single message tagging all participants
        if mentions:
            response_text = f"{extra_message}\n\n" if extra_message else ""
            response_text += "\n".join(mentions)
            response = await event.respond(response_text)
        else:
            response = await event.respond("В этом чате нет участников, кроме ботов.")

        await asyncio.sleep(60)
        await client.delete_messages(event.chat_id, response.id)


@client.on(events.NewMessage(pattern=r'(?i)^каллван(?:\s+(.+))?$'))
async def call_each(event):
    if event.is_group:

        if is_on_group_cooldown(event.chat_id):
            await event.respond(
                "Команда используется слишком часто в этом чате. Подождите 60 секунд перед повторной попыткой.")
            return

        last_command_times[event.chat_id] = time.time()

        extra_message = event.pattern_match.group(1)
        if not extra_message:
            extra_message = ""

        participants = await client.get_participants(event.chat_id, filter=tl.types.ChannelParticipantsSearch(''))
        messages_to_delete = []

        for user in participants:
            if not user.bot and user.id not in excluded_users:  # Skip bots
                emoji = get_or_assign_emoji(user.id, emojis, user_emojis)
                mention = f"[{emoji}{user.first_name}](tg://user?id={user.id})"
                response_text = f"{extra_message}\n\n{mention}" if extra_message else mention
                response = await event.respond(response_text)
                messages_to_delete.append(response.id)

        await asyncio.sleep(60)
        await client.delete_messages(event.chat_id, messages_to_delete)


@client.on(events.NewMessage(pattern=r'(?i)^анрег$'))
async def unregister_user(event):
    if event.is_group:
        user_id = event.sender_id

        excluded_users.add(user_id)

        await event.reply(f"У [{event.sender.first_name}](tg://user?id={user_id}) намечается интим, но с кем?🤔")


@client.on(events.NewMessage())
async def register_user(event):
    if event.is_group:
        user_id = event.sender_id

        if user_id in excluded_users and event.message.message != "анрег":
            excluded_users.remove(user_id)
        else:
            return


@client.on(events.NewMessage(pattern=r'(?i)^ми(?:\s+(.+))?$'))
async def mi(event):
    if event.is_group:
        emoji = get_or_assign_emoji(event.sender_id, emojis, user_emojis)

        await event.reply(f"на, {emoji}")


# Start the bot
print("Bot is running... Press Ctrl+C to stop.")
client.start()
client.run_until_disconnected()
