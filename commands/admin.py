from pyrogram import filters
from bot.utilities.filters import admin_only
from config import Config
from database.models import Admin
from bot import app

@admin_only
async def stats(client, message):
    # ... (copy your stats command implementation)

@admin_only 
async def add_admin(client, message):
    # ... (copy your addadmin command implementation)

@admin_only
async def remove_admin(client, message):
    # ... (copy your removeadmin command implementation)

# Handler group
admin_handler = filters.command(["stats", "addadmin", "removeadmin"])(stats, add_admin, remove_admin)
