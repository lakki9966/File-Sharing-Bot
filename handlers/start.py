# handlers/start.py

from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMINS
import logging
logger = logging.getLogger(__name__)

async def start_command(bot: Client, message: Message):
    user_id = message.from_user.id

    if user_id in ADMINS:
        await message.reply_text(
            "👑 Welcome Admin!\n\nUse the buttons or commands below to manage the bot.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("👤 Users", callback_data="users")],
                    [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
                    [InlineKeyboardButton("🛠 Set Expiry", callback_data="setexpiry")]
                ]
            )
        )
    else:
        await message.reply_photo(
            photo="https://te.legra.ph/file/6e8e702e9c1e7efba56ff.jpg",
            caption=(
                "**👋 Welcome to the Private File Share Bot!**\n\n"
                "📁 You can access your files from shortlinks sent to you.\n"
                "⏳ Files will be auto-deleted after 30 minutes in this chat.\n"
                "❌ You cannot use this bot to upload or store files.\n\n"
                "__Need help? Contact your admin.__"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("📂 How It Works", url="https://t.me/YourBotUsername")]
                ]
            )
        )
