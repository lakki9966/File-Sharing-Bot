# utils/admin_check.py

from database.mongodb import admins_col
from config import OWNER_ID

async def is_admin(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    admin = admins_col.find_one({"_id": user_id})
    return bool(admin)
