import secrets
import string

def generate_shortcode(length=6):
    """Generate random shortcode (e.g. zSy1WV)"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
