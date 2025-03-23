from fastapi import FastAPI, HTTPException # FastAPI to create the API, and HTTPException to handle errors.
from pydantic import BaseModel # Pydantic's BaseModel is used to define data models for request validation.
from hash_utils import generate_hash, verify_hash # utility functions for hashing operations.

# Creating a FastAPI instance.
app = FastAPI()

# -----------------------------
# Request Body Models (DTOs)
# -----------------------------

# This model defines the structure of data expected for generating a hash.
class HashRequest(BaseModel):
    data: str # Input string to hash
    algorithm: str # Hashing algorithm to use (e.g., "sha256")

class VerifyRequest(BaseModel):
    data: str  # Original string to check
    hash_value: str  # Previously generated hash to compare with
    algorithm: str # Hashing algorithm used

# -----------------------------
# API Endpoints
# -----------------------------

# Endpoint: /generate-hash
# Method: POST
# Description: Generates a Base64-encoded hash from the input data using the given algorithm.
@app.post("/generate-hash")
def generate_hash_endpoint(req: HashRequest):
    try:
        # Call the utility function to generate the hash.
        hash_val = generate_hash(req.data, req.algorithm)
        
        # Return the hash and the algorithm used.
        return {
            "hash_value": hash_val,
            "algorithm": req.algorithm
        }
    
    # If the algorithm is not supported, raise a 400 Bad Request error.
    except ValueError:
        raise HTTPException(status_code=400, detail="Unsupported hashing algorithm.")

# Endpoint: /verify-hash
# Method: POST
# Description: Verifies if a hash corresponds to the input data using the given algorithm.@app.post("/verify-hash")
@app.post("/verify-hash")
def verify_hash_endpoint(req: VerifyRequest):
    # Check if the hash matches the newly generated one from the input data.
    is_valid = verify_hash(req.data, req.hash_value, req.algorithm)

    # Return a response with a boolean and a message.
    message = "Hash matches the data." if is_valid else "Hash does not match."
    return {
        "is_valid": is_valid,
        "message": message
    }