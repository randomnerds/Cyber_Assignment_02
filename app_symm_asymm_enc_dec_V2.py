from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import os
import base64

# Create a Flask application object --app--
app = Flask(__name__)

# Store generated keys seperately
GENERATED_KEYS = {}

def generate_key(key_type, key_size):
    """
    Generate AES key for symmetric encryption and a RSA key pair for asymmetric encryption.
    """
    if key_type == "AES":
        # Generate random bytes
        key = os.urandom(key_size // 8) 
        # Assign a key ID to the generated key
        key_id = str(len(GENERATED_KEYS) + 1)
        # Convert the random byte stream into a base64-encoded object and decode it into a string
        base64_encoded_key = base64.b64encode(key).decode()
        # Store the generated key
        GENERATED_KEYS[key_id] = {"type": "AES", "key": key}

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

    else:
        return None, "Invalid key type! Please enter a valid key type."


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
        # Extract IV (First 12 bytes)
        iv = encrypted_bytes[:12]
        # Extract Tag (Middle 16 bytes)
        tag = encrypted_bytes[12:28]  
        # Extract Ciphertext (Last part)
        ciphertext = encrypted_bytes[28:] 

        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
        # Create the AES decryptor with the same AES alorithm and same key
        decryptor = cipher.decryptor()
        # Decrypt the cypertext and verify the authentication tag. The output will be in byte format
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

        return decrypted_data.decode()

    except Exception as e:
        return f"AES Decryption failed: {str(e)}"


def encrypt_rsa(public_key, plaintext):
    """
    Function for RSA encryption (asymmetric-key cryptography)
    """
    # Handle the encryption error for long messages
    # max_size = (public_key.key_size // 8) - 2 * hashes.SHA256().digest_size - 2
    
    # if len(plaintext.encode()) > max_size:
    #     return "Error: Message too long for RSA encryption. Use AES instead."
    
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
        return f"RSA Decryption failed: {str(e)}"

# API endpoint: Generate Key for AES or RSA
@app.route('/generate-key', methods=['POST'])
def generate_key_api():
    """
    This function will handle key generation requests
    """
    # Extract the JSON data from the POST request body (Key_type and key_size)
    data = request.json
    key_type = data.get("key_type")
    key_size = data.get("key_size")

    # Check the validity of the key information
    if key_type not in ["AES", "RSA"] or key_size not in [128, 192, 256, 2048, 4096]:
        return jsonify({"Error": "Invalid key type or key size"}), 400  # Bad Request

    # Generate a key according to the given specs using generate_key() function
    key_id, key_value = generate_key(key_type, key_size)

    return jsonify({"key_id": key_id, "key_value": key_value})

# API endpoint: Encryption
@app.route('/encrypt', methods=['POST'])
def encrypt():
    """
    This function will handle data encryption (both symmetric and asymmetric)
    """
    data = request.json
    key_id = data.get("key_id")
    plaintext = data.get("plaintext")
    algorithm = data.get("algorithm")

    # Check the validity of given key_id
    if key_id not in GENERATED_KEYS:
        return jsonify({"Error": "Invalid key ID"}), 400    # Bad Request

    # Extract the required key information from GENERATED_KEYS
    key_data = GENERATED_KEYS[key_id]

    try:
        # Encrypt data based on the requested algorithm type (AES or RSA)
        if algorithm == "AES" and key_data["type"] == "AES":
            ciphertext = encrypt_aes(key_data["key"], plaintext)
        elif algorithm == "RSA" and key_data["type"] == "RSA":
            ciphertext = encrypt_rsa(key_data["public_key"], plaintext)
        else:
            return jsonify({"Error": "Mismatched algorithm and key type"}), 400 # Bad Request

        return jsonify({"ciphertext": ciphertext})

    except Exception as e:
        return jsonify({"Error": f"Encryption failed: {str(e)}"}), 400  # Bad Request

# API endpoint: Decryption
@app.route('/decrypt', methods=['POST'])
def decrypt():
    """
    This function will handle data decryption (both symmetric and asymmetric)
    """
    data = request.json
    key_id = data.get("key_id")
    ciphertext = data.get("ciphertext")
    algorithm = data.get("algorithm")

    if key_id not in GENERATED_KEYS:
        return jsonify({"error": "Invalid key ID"}), 400    # Bad Request

    key_data = GENERATED_KEYS[key_id]

    try:
        # Decrypt data based on the requested algorithm type (AES or RSA)
        if algorithm == "AES" and key_data["type"] == "AES":
            plaintext = decrypt_aes(key_data["key"], ciphertext)
        elif algorithm == "RSA" and key_data["type"] == "RSA":
            plaintext = decrypt_rsa(key_data["private_key"], ciphertext)
        else:
            return jsonify({"Error": "Mismatched algorithm and key type"}), 400 # Bad Request

        return jsonify({"plaintext": plaintext})
    
    except Exception as e:
        return jsonify({"Error": f"Decryption failed: {str(e)}"}), 400  # Bad Request

if __name__ == '__main__':
    # Start the Flask web server
    app.run(debug=True)


