import secrets
import string

def generate_shortcode(length=8):
    """Generate cryptographically secure shortcode"""
    alphabet = string.ascii_letters + string.digits  # A-Za-z0-9
    return ''.join(secrets.choice(alphabet) for _ in range(length))
