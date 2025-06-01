from pyrogram import Client, filters, idle
from config import Config
from database.models import File, User
import asyncio
from datetime import datetime

class FileBot(Client):
    def __init__(self):
        super().__init__(
            "file_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            in_memory=True
        )
        self.batch_data = {}  # Temporary storage for batch uploads

app = FileBot()

# ===== SINGLE FILE UPLOAD =====
@app.on_message(filters.command("link"))
async def single_upload(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ **Reply to a file with /link**")
    
    try:
        # Forward to storage channel
        forwarded = await message.reply_to_message.forward(Config.DB_CHANNEL_ID)
        
        # Save to MongoDB
        File.add_file({
            "file_id": str(forwarded.id),
            "file_name": getattr(message.reply_to_message, "file_name", "file"),
            "uploader_id": message.from_user.id,
            "channel_msg_id": forwarded.id,
            "is_batch": False  # Mark as single file
        })
        
        # Generate link
        bot_username = (await client.get_me()).username
        await message.reply(f"""
✅ **File Stored!**
📥 **Download Link:**
`https://t.me/{bot_username}?start={forwarded.id}`
""")
    
    except Exception as e:
        await message.reply(f"⚠️ **Error:** `{str(e)}`")

# ===== BATCH UPLOAD =====
@app.on_message(filters.command("batch"))
async def start_batch(client, message):
    """Start batch upload session"""
    if not message.reply_to_message:
        return await message.reply("❌ **Reply to first file with /batch**")
    
    # Store batch info
    app.batch_data[message.from_user.id] = {
        "first_msg_id": message.reply_to_message.id,
        "last_msg_id": message.id,
        "files": []
    }
    
    await message.reply("""
📦 **Batch Mode Started!**
Now send me all files you want to include
When done, send /endbatch
""")

@app.on_message(filters.command("endbatch"))
async def end_batch(client, message):
    """Finalize batch upload"""
    user_id = message.from_user.id
    if user_id not in app.batch_data:
        return await message.reply("❌ **No active batch session!**")
    
    batch = app.batch_data[user_id]
    file_ids = list(range(batch["first_msg_id"], message.id + 1))
    
    # Process all files in batch
    saved_files = []
    async for msg in client.get_messages(
        chat_id=message.chat.id,
        message_ids=file_ids
    ):
        if msg.document or msg.photo or msg.video:
            try:
                # Forward to storage channel
                forwarded = await msg.forward(Config.DB_CHANNEL_ID)
                saved_files.append(str(forwarded.id))
                
                # Save to MongoDB
                File.add_file({
                    "file_id": str(forwarded.id),
                    "file_name": getattr(msg, "file_name", "file"),
                    "uploader_id": user_id,
                    "channel_msg_id": forwarded.id,
                    "is_batch": True,
                    "batch_id": f"{user_id}-{datetime.now().timestamp()}"
                })
            except Exception as e:
                print(f"Failed to save file: {e}")
    
    # Generate batch download link
    if saved_files:
        bot_username = (await client.get_me()).username
        batch_link = f"https://t.me/{bot_username}?start=batch-{'-'.join(saved_files)}"
        await message.reply(f"""
📦 **Batch Upload Complete!**
🔗 **Download All Files:**
`{batch_link}`
""")
    else:
        await message.reply("❌ No valid files found in batch")
    
    # Cleanup
    del app.batch_data[user_id]

# ===== START BOT =====
async def run():
    await app.start()
    print("✅ Bot is running with batch support!")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    finally:
        loop.close()
