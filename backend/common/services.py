import hashlib
import random
import string
from django.conf import settings
from django.utils import timezone


def generate_invite_code() -> str:
    """Generate a unique family invite code."""
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    code = ''
    for i in range(8):
        if i > 0 and i % 4 == 0:
            code += '-'
        code += random.choice(chars)
    return code


def generate_map_link(latitude: float, longitude: float) -> str:
    """Generate an OpenStreetMap link with a marker at the coordinates."""
    return f'https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}#map=16/{latitude}/{longitude}'


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in meters (Haversine formula)."""
    import math
    R = 6371000
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def encrypt_data(data: str) -> str:
    """Simple AES-256-like encryption for sensitive data."""
    # In production, use a proper encryption library
    # This is a placeholder
    key = settings.SECRET_KEY.encode()[:32]
    iv = ''.join(random.choice(string.ascii_letters) for _ in range(16))
    cipher = hashlib.sha256(key).hexdigest()[:32]
    # Placeholder: XOR-based for now
    encrypted = ''.join(chr(ord(c) ^ ord(cipher[i % len(cipher)])) for i, c in enumerate(data))
    return iv + ':' + encrypted.encode('utf-8').hex()


def get_emergency_numbers() -> dict:
    """Get Kyrgyzstan emergency service numbers."""
    return settings.QORGO_EMERGENCY_NUMBERS
