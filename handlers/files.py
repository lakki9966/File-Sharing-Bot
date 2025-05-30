from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from database import add_file
from utils.helpers import generate_shortlink, is_verified, rate_limited

def register(app):

    @app.on_message(filters.private & (filters.document | filters.video | filters.photo | filters.sticker))
    async def save_file(client, message: Message):
        user_id = message.from_user.id
        if not is_verified(user_id):
            return await message.reply("You are not allowed to use this bot.")

        if rate_limited(user_id):
            return await message.reply("You're sending too fast. Please wait a few seconds.")

        sent = await message.copy(Config.DATABASE_CHANNEL)
        shortlink = generate_shortlink()
        add_file(str(message.id), sent.id, shortlink, user_id)

        btn = [[InlineKeyboardButton("📥 Download", url=f"https://t.me/{client.me.username}?start={shortlink}")]]
        await message.reply("File saved!", reply_markup=InlineKeyboardMarkup(btn))

    @app.on_message(filters.command("link"))
    async def link_cmd(client, message: Message):
        if message.reply_to_message:
            shortlink = generate_shortlink()
            sent = await message.reply_to_message.copy(Config.DATABASE_CHANNEL)
            add_file(str(message.reply_to_message.id), sent.id, shortlink, message.from_user.id)
            await message.reply(f"Shortlink: https://t.me/{client.me.username}?start={shortlink}")
        else:
            await message.reply("Reply to a file to generate a shortlink.")
