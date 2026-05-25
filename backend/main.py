# ============================================================
# FILE: backend/main.py
# PURPOSE: FastAPI web server — receives requests from React,
#          coordinates quantum key gen, encryption, steganography
# ============================================================

import os
import uuid
import shutil
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException

# FastAPI    → the web framework
# File       → represents an uploaded file in the request
# UploadFile → wraps the file with metadata (filename, content_type)
# Form       → reads text fields from multipart form data
# HTTPException → sends error responses (400, 500, etc.)

from fastapi.middleware.cors import CORSMiddleware
# CORSMiddleware → allows the React frontend (different port) to call this API
# Without this, browsers block cross-origin requests

from fastapi.responses import FileResponse
# FileResponse → sends a file (the stego image) back to the frontend

# ── Import our own modules ─────────────────────────────────────────────────
from quantum.quantum_key import generate_quantum_key
from encryption.aes_encrypt import encrypt_message, decrypt_message
from steganography.stego import hide_data, extract_data

# ── Create the FastAPI application ────────────────────────────────────────
app = FastAPI(
    title="Quantum Stego API",
    description="Quantum-Inspired Secure Image Steganography Backend",
    version="1.0.0"
)

# ── Configure CORS (Cross-Origin Resource Sharing) ────────────────────────
# React runs on http://localhost:5173
# FastAPI runs on http://localhost:8000
# Without CORS, browser blocks the communication
# ── Configure CORS (Cross-Origin Resource Sharing) ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Create uploads directory ──────────────────────────────────────────────
# This folder temporarily stores uploaded images during processing
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Create if not exists, do nothing if already exists

# ── In-memory Key Store ───────────────────────────────────────────────────
# Stores generated quantum keys mapped by a unique key_id
# key_id (str UUID) → key (bytes)
# NOTE: In production, use a secure database (Redis, PostgreSQL with encryption)
# This in-memory store is lost when the server restarts
KEY_STORE: dict = {}


# ════════════════════════════════════════════════════════════════════════════
# ENDPOINT 1: GET /
# Health check — confirms server is running
# ════════════════════════════════════════════════════════════════════════════
@app.get("/")
def root():
    return {"status": "ok", "message": "Quantum Stego API is running"}


# ════════════════════════════════════════════════════════════════════════════
# ENDPOINT 2: GET /generate-key
# Runs Qiskit quantum circuit → generates AES key → stores it → returns key_id
# ════════════════════════════════════════════════════════════════════════════
@app.get("/generate-key")
def get_quantum_key():
    """
    Generates a quantum-inspired AES key and stores it server-side.

    FLOW:
    ──────
    1. Call generate_quantum_key() → runs Qiskit simulation
    2. Get back: key (bytes) + bits (list of 0s/1s)
    3. Generate a unique key_id (UUID) for this key
    4. Store key in KEY_STORE mapped to key_id
    5. Return key_id and bits (for visualization in frontend)

    The key itself is NEVER sent to the frontend for security.
    Only the key_id is shared — the frontend uses it like a reference.

    RESPONSE:
    ──────────
    {
      "key_id": "550e8400-e29b-41d4-a716...",   ← unique identifier
      "quantum_bits": [1,0,1,1,0,...],            ← first 64 bits (for visualization)
      "message": "Quantum key generated successfully"
    }
    """
    try:
        # Run the quantum circuit and get the key
        key, bits = generate_quantum_key()
        # key  = b'a8h3jKx2Lm...=='  (44 chars, Fernet-compatible)
        # bits = [1,0,1,1,0,...]     (256 values)

        # Generate a unique ID for this key (UUID4 = random UUID)
        key_id = str(uuid.uuid4())
        # Example: "550e8400-e29b-41d4-a716-446655440000"

        # Store key in memory (key never leaves the server)
        KEY_STORE[key_id] = key

        return {
            "key_id": key_id,
            "quantum_bits": bits[:64],   # Send only first 64 bits for display
            "message": "Quantum key generated successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Key generation failed: {str(e)}")


# ════════════════════════════════════════════════════════════════════════════
# ENDPOINT 3: POST /encrypt
# Receives image + message + key_id → encrypts → hides in image → returns stego image
# ════════════════════════════════════════════════════════════════════════════
@app.post("/encrypt")
async def encrypt(
    image: UploadFile = File(...),      # The cover image uploaded by user
    message: str = Form(...),           # The secret text message
    key_id: str = Form(...)             # The UUID returned by /generate-key
):
    """
    Encrypts a message and hides it inside an image.

    COMPLETE FLOW:
    ───────────────
    1. Validate key_id exists in KEY_STORE
    2. Save uploaded image to disk temporarily
    3. Encrypt the message using the quantum AES key → ciphertext bytes
    4. Hide ciphertext bytes in image pixels using LSB steganography
    5. Return the stego image as a downloadable PNG file
    6. Clean up temp input file

    REQUEST (multipart/form-data):
    ──────────────────────────────
    image   : file   → the original cover image (PNG or JPG)
    message : string → secret message e.g. "Meet at airport gate B7"
    key_id  : string → UUID from /generate-key response

    RESPONSE:
    ──────────
    PNG file (binary download) → the stego image with hidden encrypted message
    """

    # ── Step 1: Validate key_id ────────────────────────────────────────────
    if key_id not in KEY_STORE:
        raise HTTPException(
            status_code=400,
            detail="Invalid key_id. Please generate a new quantum key first."
        )

    # Retrieve the stored quantum key
    key = KEY_STORE[key_id]

    # ── Step 2: Save uploaded image to disk ────────────────────────────────
    # Generate unique filenames to avoid conflicts when multiple users use the API
    unique_id = str(uuid.uuid4())
    input_ext = Path(image.filename).suffix if image.filename else ".png"
    input_path = UPLOAD_DIR / f"input_{unique_id}{input_ext}"
    output_path = UPLOAD_DIR / f"stego_{unique_id}.png"
    # Always save output as PNG to preserve LSBs (JPEG would destroy them)

    # Write uploaded file bytes to disk
    with open(input_path, "wb") as f:
        shutil.copyfileobj(image.file, f)
    # shutil.copyfileobj efficiently copies file in chunks (good for large files)

    try:
        # ── Step 3: Encrypt the message ─────────────────────────────────────
        # encrypt_message returns Fernet token (bytes)
        # Example: b'gAAAAABo7sjkL9d....'
        ciphertext = encrypt_message(message, key)

        # ── Step 4: Hide ciphertext in image using LSB steganography ─────────
        hide_data(str(input_path), ciphertext, str(output_path))
        # output_path now contains the stego image with hidden encrypted data

        # ── Step 5: Send stego image back to frontend ──────────────────────
        # FileResponse streams the file directly
        # media_type="image/png" tells browser it's a PNG file
        # filename="stego_image.png" sets the default download filename
        return FileResponse(
            path=str(output_path),
            media_type="image/png",
            filename="stego_image.png"
        )

    except ValueError as e:
        # Known errors (image too small, etc.)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Unexpected errors
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")

    finally:
        # ── Cleanup: always remove the input file ──────────────────────────
        # The output stego file stays until downloaded (FileResponse handles it)
        if input_path.exists():
            os.remove(input_path)


# ════════════════════════════════════════════════════════════════════════════
# ENDPOINT 4: POST /decrypt
# Receives stego image + key_id → extracts LSBs → decrypts → returns message
# ════════════════════════════════════════════════════════════════════════════
@app.post("/decrypt")
async def decrypt(
    image: UploadFile = File(...),      # The stego image
    key_id: str = Form(...)             # The same key_id used during encryption
):
    """
    Extracts the hidden message from a stego image and decrypts it.

    COMPLETE FLOW:
    ───────────────
    1. Validate key_id exists in KEY_STORE
    2. Save uploaded stego image to disk temporarily
    3. Extract hidden binary data using LSB extraction
    4. Reconstruct ciphertext bytes from binary
    5. Decrypt ciphertext using the stored quantum AES key
    6. Return the original plain text message
    7. Cleanup temp file

    REQUEST (multipart/form-data):
    ──────────────────────────────
    image  : file   → the stego PNG image
    key_id : string → the UUID from when the message was originally encrypted

    RESPONSE:
    ──────────
    {
      "message": "Meet at airport gate B7"   ← the original secret message
    }
    """

    # ── Step 1: Validate key_id ────────────────────────────────────────────
    if key_id not in KEY_STORE:
        raise HTTPException(
            status_code=400,
            detail="Key not found. The server may have restarted, or wrong key_id provided."
        )

    key = KEY_STORE[key_id]

    # ── Step 2: Save stego image to disk ──────────────────────────────────
    unique_id = str(uuid.uuid4())
    input_ext = Path(image.filename).suffix if image.filename else ".png"
    input_path = UPLOAD_DIR / f"decrypt_{unique_id}{input_ext}"

    with open(input_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    try:
        # ── Step 3 & 4: Extract ciphertext from image using LSB extraction ──
        ciphertext = extract_data(str(input_path))
        # ciphertext = b'gAAAAABo7sjkL9d....' (raw Fernet token bytes)

        # ── Step 5: Decrypt using stored quantum key ───────────────────────
        plaintext = decrypt_message(ciphertext, key)
        # plaintext = "Meet at airport gate B7"

        # ── Step 6: Return the recovered message ───────────────────────────
        return {"message": plaintext}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")

    finally:
        # ── Cleanup: remove temp stego image ──────────────────────────────
        if input_path.exists():
            os.remove(input_path)
