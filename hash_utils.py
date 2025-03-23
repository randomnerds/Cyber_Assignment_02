import base64 # Used to encode binary hash into readable Base64 format
import hashlib # Provides access to secure hash functions (e.g., SHA256, SHA512)

# Generates a Base64-encoded hash from input data using the given algorithm.
def generate_hash(data: str, algorithm: str) -> str:
    # Get the appropriate hash function from hashlib using the algorithm name (e.g., "sha256")
    hasher = getattr(hashlib, algorithm.lower(), None)

    # If the algorithm is not available, raise an error.
    if not hasher:
        raise ValueError("Unsupported hashing algorithm")
    
    # Encode the input string to bytes and generate the hash digest.
    hash_bytes = hasher(data.encode()).digest()
    
    # Encode the hash bytes to Base64 so it can be returned as a string.
    return base64.b64encode(hash_bytes).decode()

# Verifies if the given hash value matches the hash of the input data.
def verify_hash(data: str, hash_value: str, algorithm: str) -> bool:
    try:
        # Generate a new hash from the input data using the same algorithm.
        new_hash = generate_hash(data, algorithm)

        # Compare the newly generated hash to the one provided.
        return new_hash == hash_value
    
    # If anything goes wrong (e.g., unsupported algorithm), return False.
    except Exception:
        return False