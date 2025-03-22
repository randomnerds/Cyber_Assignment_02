# Cyber_Assignment_02

## Cryptographic API Development

### 🔹 1. Clone the Repository

### 🔹 2. Create and Activate a Conda Environment
```bash
conda create --name cyber_dev python=3.10.16 -y
conda activate cyber_dev
```

### 🔹 3. Install Dependencies
```bash
python -m pip install -r requirements_api1.txt
```

### 🔹 4. Run API Server
#### Local testing:
```bash
uvicorn app_symm_asymm_enc_dec_V2:app --reload
```
#### External testing:
```bash
uvicorn app_symm_asymm_enc_dec_V2:app --host 0.0.0.0 --port 5000
```

## Hashing and Verifying Hashed-token

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

### 🔹 4. Run API Server
#### Local testing:
```bash
uvicorn hash_main:app --reload
```
#### External testing:
```bash
uvicorn hash_main:app --host 0.0.0.0 --port 5000
```
