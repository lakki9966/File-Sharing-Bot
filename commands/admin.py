from pyrogram import filters
from utilities.filters import admin_only
from config import Config
from database.models import Admin, User, File

app = None  # Will be set by main.py

@admin_only
async def stats(client, message):
    try:
        stats_text = f"""
📊 Bot Statistics:
├ Files: {File.collection.count_documents({})}
├ Users: {User.collection.count_documents({})}
└ Admins: {Admin.collection.count_documents({})}

⚙️ Configuration:
├ DB Channel: {Config.DB_CHANNEL_ID}
└ Owner ID: {Config.OWNER_ID}
"""
        await message.reply(stats_text)
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)}")

@admin_only 
async def add_admin(client, message):
    try:
        if len(message.command) < 2:
            return await message.reply("❌ Usage: /addadmin [user_id]")
        
        new_admin = int(message.command[1])
        Admin.add_admin(new_admin)
        await message.reply(f"✅ Added admin: {new_admin}")
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)}")
        logger.exception("Addadmin failed")

@admin_only
async def remove_admin(client, message):
    try:
        if len(message.command) < 2:
            return await message.reply("❌ Usage: /removeadmin [user_id]")
        
        admin_id = int(message.command[1])
        Admin.collection.delete_one({"user_id": admin_id})
        await message.reply(f"✅ Removed admin: {admin_id}")
    except Exception as e:
        await message.reply(f"⚠️ Error: {str(e)}")
        logger.exception("Removeadmin failed")

# Handler group
admin_handler = filters.command(["stats", "addadmin", "removeadmin"])(stats, add_admin, remove_admin)
