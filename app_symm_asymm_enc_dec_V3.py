from flask import Flask, request, jsonify
from pydantic import BaseModel, Field, ValidationError
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import os
import base64

# Create a Flask application object --app--
app = Flask(__name__)

# Store generated keys seperately
GENERATED_KEYS = {}

# DTOs for structured data validation
class KeyGenerationRequest(BaseModel):
    key_type: str = Field(..., pattern="^(AES|RSA)$", description="Key type must be AES or RSA")
    key_size: int = Field(..., description="Key size in bits")

class EncryptionRequest(BaseModel):
    key_id: str = Field(..., description="Key identifier")
    plaintext: str = Field(..., description="Plaintext to encrypt")
    algorithm: str = Field(..., pattern="^(AES|RSA)$", description="Encryption algorithm must be AES or RSA")

class DecryptionRequest(BaseModel):
    key_id: str = Field(..., description="Key identifier")
    ciphertext: str = Field(..., description="Encrypted data in base64 format")
    algorithm: str = Field(..., pattern="^(AES|RSA)$", description="Decryption algorithm must be AES or RSA")


def generate_key(key_type: str, key_size: int):
    """
    Generate AES key for symmetric encryption and a RSA key pair for asymmetric encryption.
    """
    if key_type == "AES":
        # Generate random bytes
        key = os.urandom(key_size // 8)
        # Assign a key ID to the generated key
        key_id = str(len(GENERATED_KEYS) + 1)
        # Store the generated key
        GENERATED_KEYS[key_id] = {"type": "AES", "key": key}
        # Convert the random byte stream into a base64-encoded object and decode it into a string
        base64_encoded_key = base64.b64encode(key).decode()

        return key_id, base64_encoded_key
    
    elif key_type == "RSA":
        # Generate the private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        # Extract the public key from generated private key
        public_key = private_key.public_key()

        key_id = str(len(GENERATED_KEYS) + 1)

        GENERATED_KEYS[key_id] = {"type": "RSA", "private_key": private_key, "public_key": public_key}
        
        return key_id, "RSA key pair is generated."
    
    return None, "Invalid key type!"


def encrypt_aes(key, plaintext):
    """
    Function for AES encryption (symmetric-key cryptography)
    """
    # Generate a 12 byte random initialization vector for AES Counter mode
    iv = os.urandom(12)
    # Create a Cipher object with AES algorithm and GCM mode
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
    # Create an encryption object to handle the encryption process
    encryptor = cipher.encryptor()
    # Generate the cypertext
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    # Combining initialization vector, authentication tag, encrypted message together and encode it using base-64 encoding and decode it into a regular string
    encrypted_data = base64.b64encode(iv + encryptor.tag + ciphertext).decode()
    
    return encrypted_data

def decrypt_aes(key, encrypted_data):
    """
    Function for AES decryption (symmetric-key cryptography)
    """
    try:
        # Decode the base64-encoded encrypted data to its binary format so that we can extract iv, cypertext and authentication tag
        encrypted_bytes = base64.b64decode(encrypted_data)
        # Extract IV, tag and ciphertext
        iv, tag, ciphertext = encrypted_bytes[:12], encrypted_bytes[12:28], encrypted_bytes[28:]
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
        # Create the AES decryptor with the same AES alorithm and same key
        decryptor = cipher.decryptor()
        # Decrypt the cypertext and verify the authentication tag. The output will be in byte format
        return (decryptor.update(ciphertext) + decryptor.finalize()).decode()
    
    except Exception as e:
        return f"AES Decryption failed: {str(e)}"


def encrypt_rsa(public_key, plaintext):
    """
    Function for RSA encryption (asymmetric-key cryptography)
    """

    # Encrypt the encoded plaintext using the public key.
    # Here we use Optimal Asymmetric Encryption Padding with SHA256 hashing
    ciphertext = public_key.encrypt(
        plaintext.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return base64.b64encode(ciphertext).decode()

def decrypt_rsa(private_key, encrypted_data):
    """
    Function for RSA decryption (asymmetric-key cryptography)
    """
    try:
        # Decode the received encoded encrypted data
        encrypted_bytes = base64.b64decode(encrypted_data)
        # Decrypt the byte stream using private key and OAEP padding
        return private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode()
    
    except Exception as e:
        return f"RSA Decryption failed: {str(e)}"

# API endpoint: Generate Key for AES or RSA
@app.route('/generate-key', methods=['POST'])
def generate_key_api():
    """
    This function will handle key generation requests
    """
    # Extract the JSON data from the POST request body (Key_type and key_size)
    try:
        data = KeyGenerationRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    key_id, key_value = generate_key(data.key_type, data.key_size)
    return jsonify({"key_id": key_id, "key_value": key_value})

# API endpoint: Encryption
@app.route('/encrypt', methods=['POST'])
def encrypt():
    """
    This function will handle data encryption (both symmetric and asymmetric)
    """
    try:
        data = EncryptionRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    if data.key_id not in GENERATED_KEYS:
        return jsonify({"error": "Invalid key ID"}), 400
    key_info = GENERATED_KEYS[data.key_id]
    if data.algorithm != key_info["type"]:
        return jsonify({"error": "Algorithm mismatch"}), 400
    if data.algorithm == "AES":
        ciphertext = encrypt_aes(key_info["key"], data.plaintext)
    else:
        ciphertext = encrypt_rsa(key_info["public_key"], data.plaintext)
    return jsonify({"ciphertext": ciphertext})

# API endpoint: Decryption
@app.route('/decrypt', methods=['POST'])
def decrypt():
    """
    This function will handle data decryption (both symmetric and asymmetric)
    """
    try:
        data = DecryptionRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    if data.key_id not in GENERATED_KEYS:
        return jsonify({"error": "Invalid key ID"}), 400
    key_info = GENERATED_KEYS[data.key_id]
    if data.algorithm != key_info["type"]:
        return jsonify({"error": "Algorithm mismatch"}), 400
    if data.algorithm == "AES":
        plaintext = decrypt_aes(key_info["key"], data.ciphertext)
    else:
        plaintext = decrypt_rsa(key_info["private_key"], data.ciphertext)
    return jsonify({"plaintext": plaintext})

if __name__ == '__main__':
    # Start the Flask web server
    app.run(debug=True)
