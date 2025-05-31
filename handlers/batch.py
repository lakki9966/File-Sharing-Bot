# handlers/batch.py
from pyrogram import filters
from database.models import File

@app.on_message(filters.command("batch"))
async def batch_handler(client, message):
    if not message.reply_to_message:
        return await message.reply("Please reply to multiple files with /batch")
    
    # Store all messages in the batch
    first_msg_id = last_msg_id = None
    async for msg in client.iter_history(
        message.chat.id,
        offset_id=message.reply_to_message.id,
        reverse=True
    ):
        if not first_msg_id:
            first_msg_id = msg.id
        last_msg_id = msg.id
        
        # Save each file to database
        File().add_file(
            file_id=msg.document.file_id if msg.document else msg.photo.file_id,
            file_name=msg.document.file_name if msg.document else "photo.jpg",
            uploader_id=message.from_user.id,
            message_id=msg.id
        )
    
    # Generate batch shortlink
    batch_id = generate_shortcode()
    # Save batch info to database
    # Return shortlink to user
