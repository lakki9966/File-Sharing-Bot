# utils/shortener.py

import random
import string

def generate_shortlink(length=7):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
