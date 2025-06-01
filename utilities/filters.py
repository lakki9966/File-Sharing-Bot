from pyrogram import filters
from database.models import Admin

def admin_filter(_, __, message):
    if not message.from_user:
        return False
    return Admin.is_admin(message.from_user.id)

admin_only = filters.create(admin_filter)
