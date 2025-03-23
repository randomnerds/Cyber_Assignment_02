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

**Generate Key**
* Method: ```POST```
* URL: ```http://127.0.0.1:5000/generate-key```
* Body (raw, JSON):
```bash
{
  "key_type": "AES",
  "key_size": "256"
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
We have already run the above command in an AWS EC2 Instance and hosted the API under the URL ```http://16.170.240.86:5000```. 

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
