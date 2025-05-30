from pyrogram import filters
from pyrogram.types import Message
from utils.helpers import is_verified

def register(app):

    @app.on_message(filters.command("batch"))
    async def batch_cmd(client, message: Message):
        if not is_verified(message.from_user.id):
            return await message.reply("You are not verified.")
        await message.reply("Batch upload not yet implemented.")  # Placeholder
