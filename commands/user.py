from pyrogram import filters
from bot import app
from database.models import User, File
import logging

logger = logging.getLogger(__name__)

async def start(client, message):
    if len(message.command) > 1:
        param = message.command[1]
        
        if param.startswith("batch-"):
            batch_id = param.split("-")[1]
            batch_files = File.collection.find({"batch_id": batch_id})
            
            sent_count = 0
            for file_data in batch_files:
                try:
                    await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=Config.DB_CHANNEL_ID,
                        message_id=int(file_data["file_id"])
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send file {file_data['file_id']}: {e}")
            
            await message.reply(f"📦 Sent {sent_count} files from batch")
            return
            
        file_data = File.collection.find_one({"random_id": param})
        if file_data:
            try:
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=Config.DB_CHANNEL_ID,
                    message_id=int(file_data["file_id"])
                )
                return
            except Exception as e:
                logger.error(f"File send error: {e}")

    User.add_user(message.from_user.id, message.from_user.username)
    await message.reply("🌟 Welcome to File Share Bot!\nUse /help for all commands")

async def help(client, message):
    help_text = """
📚 Available Commands:

📁 File Sharing:
/link - Generate file link (reply to any media)
/batch - Start batch upload (reply to first file)
/endbatch - Finish batch upload

👤 Account:
/myfiles - View your uploaded files

👑 Admin Commands:
/stats - View bot statistics
/addadmin [user_id] - Add admin
/removeadmin [user_id] - Remove admin
/setexpiry [minutes] - Set file expiry
/verify - Check your admin status
"""
    await message.reply(help_text)

# Handlers
start_handler = filters.command("start")(start)
help_handler = filters.command("help")(help)
