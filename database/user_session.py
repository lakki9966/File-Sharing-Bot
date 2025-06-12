# database/user_session.py

from database.mongodb import session_col
from datetime import datetime

async def save_user_session(user_id, shortlink, message_ids):
    session_col.update_one(
        {"user_id": user_id, "shortlink": shortlink},
        {
            "$set": {
                "access_time": datetime.utcnow(),
                "message_ids": message_ids
            }
        },
        upsert=True
    )

async def get_expired_sessions(minutes):
    from datetime import timedelta
    now = datetime.utcnow()
    expired_time = now - timedelta(minutes=minutes)

    return session_col.find({"access_time": {"$lte": expired_time}})

async def delete_session(user_id, shortlink):
    session_col.delete_one({"user_id": user_id, "shortlink": shortlink})
