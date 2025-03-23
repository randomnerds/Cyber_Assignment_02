# Cyber_Assignment_02

### 🔹 1. Clone the Repository

### 🔹 2. Create and Activate a Conda Environment
```bash
conda create --name crypto python=3.10
conda activate crypto
```

### 🔹 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

## Cryptographic API Development

### 🔹 4. Run API Server
#### Local testing:
```bash
python app_symm_asymm_enc_dec_V2.py
```
#### **Test Using Postman**:

**Key Generation**
* Method: ```POST```
* URL: ```http://127.0.0.1:5000/generate-key```
* Body (raw, JSON):
```bash
{
  "key_type": "AES",
  "key_size": "256"
}
```
For symmetric-key encryption, AES keys can be generated using key sizes of 128, 192 and 256 bits. For asymmetric-key encryption, RSA key pairs can be generated using key sizes of 2048 and 4096 bits.

**Data Encryption**
* Method: ```POST```
* URL: ```http://127.0.0.1:5000/encrypt```
* Body (raw, JSON):
```bash
{
  "key_id": "1",
  "plaintext": "message-to-encrypt",
  "algorithm": "AES"
}
```

**Data Decryption**
* Method: ```POST```
* URL: ```http://127.0.0.1:5000/decrypt```
* Body (raw, JSON):
```bash
{
  "key_id": "1",
  "ciphertext": "base64-encoded-ciphertext",
  "algorithm": "AES"
}
```
For encryption and decryption parts also, both AES and RSA methods can be used with respective key IDs.

#### **B. Run API Server Externally**:
We have already run the above command in an AWS EC2 Instance and hosted the API under the URL ```http://16.170.240.86:8000``` for key generation, encryption and decryption. Do note that port `8000` is used for the cyptographic API operations. 

#### **Test Using Postman**:

**Key Generation**
* Method: ```POST```
* URL: ```http://16.170.240.86:8000/generate-key```
* Body (raw, JSON):
```bash
{
  "key_type": "AES",
  "key_size": "256"
}
```
For symmetric-key encryption, AES keys can be generated using key sizes of 128, 192 and 256 bits. For asymmetric-key encryption, RSA key pairs can be generated using key sizes of 2048 and 4096 bits.

**Data Encryption**
* Method: ```POST```
* URL: ```http://16.170.240.86:8000/encrypt```
* Body (raw, JSON):
```bash
{
  "key_id": "1",
  "plaintext": "message-to-encrypt",
  "algorithm": "AES"
}
```

**Data Decryption**
* Method: ```POST```
* URL: ```http://16.170.240.86:8000/decrypt```
* Body (raw, JSON):
```bash
{
  "key_id": "1",
  "ciphertext": "base64-encoded-ciphertext",
  "algorithm": "AES"
}
```
For encryption and decryption parts also, both AES and RSA methods can be used with respective key IDs.

## Hashing and Verifying Hashed-token

#### **A. Run API Server Locally**
```bash
uvicorn hash_main:app --reload
```
#### **Test Using Postman**:

**Generate Hash**
* Method: ```POST```
* URL: ```http://127.0.0.1:8000/generate-hash```
* Body (raw, JSON):
```bash
{
  "data": "Hello World",
  "algorithm": "sha256"
}
```

**Verifying Hashed-token**
* Method: ```POST```
* URL: ```http://127.0.0.1:8000/verify-hash```
* Body (raw, JSON):
```bash
{
  "data": "Hello World",
  "hash_value": "base64-encoded-hash",
  "algorithm": "sha256"
}
```

#### **B. Run API Server Externally**:
```bash
uvicorn hash_main:app --host 0.0.0.0 --port 5000
```
We have already run the above command in an AWS EC2 Instance and hosted the API under the URL ```http://16.170.240.86:5000``` for generating the hash and verifying the hashed-token. Do note that port `5000` is used for the hash implementation. 

#### **Test Using Postman**:

**Generate Hash**
* Method: ```POST```
* URL: ```http://16.170.240.86:5000/generate-hash```
* Body (raw, JSON):
```bash
{
  "data": "Hello World",
  "algorithm": "sha256"
}
```

**Verifying Hashed-token**
* Method: ```POST```
* URL: ```http://16.170.240.86:5000/verify-hash```
* Body (raw, JSON):
```bash
{
  "data": "Hello World",
  "hash_value": "base64-encoded-hash",
  "algorithm": "sha256"
}
```
