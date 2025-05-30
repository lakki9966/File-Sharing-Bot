import string
import random
from config import Config

def generate_shortlink(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def is_verified(user_id):
    return user_id in Config.ALLOWED_USERS

def rate_limited(user_id, cache={}):
    import time
    now = time.time()
    if user_id in cache and now - cache[user_id] < 5:  # 5-second delay
        return True
    cache[user_id] = now
    return False
