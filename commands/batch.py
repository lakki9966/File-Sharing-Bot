from pyrogram import filters
from bot import app
from config import Config
from database.models import File
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def start_batch(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Please reply to the first file with /batch")
    
    if message.from_user.id in app.batch_data:
        return await message.reply("❌ You already have an active batch. End it with /endbatch first.")
    
    batch_id = app.generate_random_id()
    app.batch_data[message.from_user.id] = {
        "first_id": message.reply_to_message.id,
        "chat_id": message.chat.id,
        "batch_id": batch_id,
        "files": []
    }
    await message.reply(
        f"📦 Batch upload started! ID: {batch_id}\n"
        f"Now send more files and type /endbatch when done"
    )

async def collect_batch_files(client, message):
    if message.from_user.id not in app.batch_data:
        return
    
    app.batch_data[message.from_user.id]["files"].append(message.id)
    await message.reply("✅ File added to batch. Send more or /endbatch when done")

async def end_batch(client, message):
    user_data = app.batch_data.get(message.from_user.id)
    if not user_data:
        return await message.reply("❌ No active batch session!")
    
    try:
        file_count = 0
        first_msg = await client.get_messages(
            chat_id=user_data["chat_id"],
            message_ids=user_data["first_id"]
        )
        
        if first_msg and (first_msg.document or first_msg.photo or first_msg.video or 
                         first_msg.sticker or first_msg.animation or first_msg.text):
            forwarded = await first_msg.forward(Config.DB_CHANNEL_ID)
            File.add_file({
                "file_id": str(forwarded.id),
                "random_id": app.generate_random_id(),
                "type": "batch",
                "uploader_id": message.from_user.id,
                "batch_id": user_data["batch_id"],
                "timestamp": datetime.now(),
                "media_type": app.get_media_type(first_msg)
            })
            file_count += 1
        
        for msg_id in user_data["files"]:
            try:
                msg = await client.get_messages(
                    chat_id=user_data["chat_id"],
                    message_ids=msg_id
                )
                
                if msg and (msg.document or msg.photo or msg.video or 
                           msg.sticker or msg.animation or msg.text):
                    forwarded = await msg.forward(Config.DB_CHANNEL_ID)
                    File.add_file({
                        "file_id": str(forwarded.id),
                        "random_id": app.generate_random_id(),
                        "type": "batch",
                        "uploader_id": message.from_user.id,
                        "batch_id": user_data["batch_id"],
                        "timestamp": datetime.now(),
                        "media_type": app.get_media_type(msg)
                    })
                    file_count += 1
            except Exception as e:
                logger.error(f"Error processing message {msg_id}: {e}")
                continue

        if file_count == 0:
            return await message.reply("❌ No valid files found in batch!")
        
        bot_username = (await client.get_me()).username
        await message.reply(
            f"📦 Batch completed successfully!\n"
            f"• Files processed: {file_count}\n"
            f"• Batch ID: {user_data['batch_id']}\n"
            f"🔗 Download link: t.me/{bot_username}?start=batch-{user_data['batch_id']}"
        )
    except Exception as e:
        await message.reply("⚠️ Failed to complete batch. Please try again.")
        logger.error(f"Batch processing failed: {e}")
    finally:
        if message.from_user.id in app.batch_data:
            del app.batch_data[message.from_user.id]

# Handlers
batch_handler = filters.command("batch")(start_batch)
collect_handler = (
    (filters.document | filters.photo | filters.video | 
     filters.sticker | filters.animation | filters.text) &
    ~filters.command("endbatch")
)(collect_batch_files)
endbatch_handler = filters.command("endbatch")(end_batch)
