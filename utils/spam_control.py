from time import time
from collections import defaultdict

# In-memory tracker
user_msg_times = defaultdict(list)
LIMIT = 5   # Max messages
WINDOW = 1  # In how many seconds
MUTE_TIME = 300  # Mute 5 mins

# Track muted users
muted_users = {}

async def check_spam(bot, message):
    user_id = message.from_user.id
    now = time()

    # Check if muted
    if user_id in muted_users and now < muted_users[user_id]:
        return True

    # Update message timestamps
    user_msg_times[user_id].append(now)
    user_msg_times[user_id] = [t for t in user_msg_times[user_id] if now - t < WINDOW]

    if len(user_msg_times[user_id]) > LIMIT:
        muted_users[user_id] = now + MUTE_TIME
        await message.reply_text("⛔ Too many messages! Try again in 5 mins.")
        return True

    return False
