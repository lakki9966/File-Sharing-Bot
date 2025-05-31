# utils/shortlink.py
import secrets
import string

def generate_shortcode(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def create_shortlink(bot_username, file_id):
    return f"https://t.me/{bot_username}?start={file_id}"
