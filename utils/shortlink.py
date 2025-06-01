import secrets
import string

def generate_shortcode(length=6):
    """Generate random case-sensitive shortcode"""
    chars = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(secrets.choice(chars) for _ in range(length))
