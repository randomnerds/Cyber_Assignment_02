import base64
import hashlib

def generate_hash(data: str, algorithm: str) -> str:
    hasher = getattr(hashlib, algorithm.lower(), None)
    if not hasher:
        raise ValueError("Unsupported hashing algorithm")
    hash_bytes = hasher(data.encode()).digest()
    return base64.b64encode(hash_bytes).decode()

def verify_hash(data: str, hash_value: str, algorithm: str) -> bool:
    try:
        new_hash = generate_hash(data, algorithm)
        return new_hash == hash_value
    except Exception:
        return False