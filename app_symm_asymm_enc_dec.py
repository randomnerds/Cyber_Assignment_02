from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import os
import base64

app = Flask(__name__)

# In-memory storage for generated keys
KEY_STORAGE = {}

# Function to generate AES or RSA key
def generate_key(key_type, key_size):
    if key_type == "AES":
        key = os.urandom(key_size // 8)  # Generate random bytes
        key_id = str(len(KEY_STORAGE) + 1)
        key_base64 = base64.b64encode(key).decode()
        KEY_STORAGE[key_id] = {"type": "AES", "key": key}
        return key_id, key_base64

    elif key_type == "RSA":
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        public_key = private_key.public_key()
        key_id = str(len(KEY_STORAGE) + 1)
        KEY_STORAGE[key_id] = {"type": "RSA", "private_key": private_key, "public_key": public_key}
        return key_id, "RSA key pair generated"

    else:
        return None, "Invalid key type"

# AES Encryption function
def encrypt_aes(key, plaintext):
    iv = os.urandom(12)  # AES-GCM requires a 12-byte IV
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return base64.b64encode(iv + encryptor.tag + ciphertext).decode()

# AES Decryption function
def decrypt_aes(key, encrypted_data):
    try:
        encrypted_bytes = base64.b64decode(encrypted_data)
        iv = encrypted_bytes[:12]  # Extract IV (First 12 bytes)
        tag = encrypted_bytes[12:28]  # Extract Tag (Last 16 bytes)
        ciphertext = encrypted_bytes[28:]  # Extract Ciphertext (Middle part)

        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted_data.decode()

    except Exception as e:
        return f"Decryption failed: {str(e)}"

# RSA Encryption function
def encrypt_rsa(public_key, plaintext):
    ciphertext = public_key.encrypt(
        plaintext.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(ciphertext).decode()

# RSA Decryption function
def decrypt_rsa(private_key, encrypted_data):
    try:
        encrypted_bytes = base64.b64decode(encrypted_data)
        plaintext = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode()
    except Exception as e:
        return f"Decryption failed: {str(e)}"

# API: Generate Key (AES or RSA)
@app.route('/generate-key', methods=['POST'])
def generate_key_api():
    data = request.json
    key_type = data.get("key_type")
    key_size = data.get("key_size")

    if key_type not in ["AES", "RSA"] or key_size not in [128, 192, 256, 2048, 4096]:
        return jsonify({"error": "Invalid key type or size"}), 400

    key_id, key_value = generate_key(key_type, key_size)
    return jsonify({"key_id": key_id, "key_value": key_value})

# API: Encrypt Data
@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.json
    key_id = data.get("key_id")
    plaintext = data.get("plaintext")
    algorithm = data.get("algorithm")

    if key_id not in KEY_STORAGE:
        return jsonify({"error": "Invalid key ID"}), 400

    key_data = KEY_STORAGE[key_id]

    try:
        if algorithm == "AES" and key_data["type"] == "AES":
            ciphertext = encrypt_aes(key_data["key"], plaintext)
        elif algorithm == "RSA" and key_data["type"] == "RSA":
            ciphertext = encrypt_rsa(key_data["public_key"], plaintext)
        else:
            return jsonify({"error": "Mismatched algorithm and key type"}), 400

        return jsonify({"ciphertext": ciphertext})

    except Exception as e:
        return jsonify({"error": f"Encryption failed: {str(e)}"}), 400

# API: Decrypt Data
@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.json
    key_id = data.get("key_id")
    ciphertext = data.get("ciphertext")
    algorithm = data.get("algorithm")

    if key_id not in KEY_STORAGE:
        return jsonify({"error": "Invalid key ID"}), 400

    key_data = KEY_STORAGE[key_id]

    try:
        if algorithm == "AES" and key_data["type"] == "AES":
            plaintext = decrypt_aes(key_data["key"], ciphertext)
        elif algorithm == "RSA" and key_data["type"] == "RSA":
            plaintext = decrypt_rsa(key_data["private_key"], ciphertext)
        else:
            return jsonify({"error": "Mismatched algorithm and key type"}), 400

        return jsonify({"plaintext": plaintext})
    
    except Exception as e:
        return jsonify({"error": f"Decryption failed: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True)


