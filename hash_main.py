from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from hash_utils import generate_hash, verify_hash

app = FastAPI()

# Data Transfer Objects (DTOs)
class HashRequest(BaseModel):
    data: str
    algorithm: str

class VerifyRequest(BaseModel):
    data: str
    hash_value: str
    algorithm: str

# POST /generate-hash
@app.post("/generate-hash")
def generate_hash_endpoint(req: HashRequest):
    try:
        hash_val = generate_hash(req.data, req.algorithm)
        return {
            "hash_value": hash_val,
            "algorithm": req.algorithm
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Unsupported hashing algorithm.")

# POST /verify-hash
@app.post("/verify-hash")
def verify_hash_endpoint(req: VerifyRequest):
    is_valid = verify_hash(req.data, req.hash_value, req.algorithm)
    message = "Hash matches the data." if is_valid else "Hash does not match."
    return {
        "is_valid": is_valid,
        "message": message
    }