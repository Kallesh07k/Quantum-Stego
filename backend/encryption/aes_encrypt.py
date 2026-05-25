# ============================================================
# FILE: backend/encryption/aes_encrypt.py
# PURPOSE: Encrypt and decrypt messages using Fernet (AES)
# ============================================================

from cryptography.fernet import Fernet, InvalidToken
# Fernet = symmetric encryption built on top of AES-128-CBC + HMAC-SHA256
# InvalidToken = exception raised when decryption fails (wrong key / tampered data)


def encrypt_message(plaintext: str, key: bytes) -> bytes:
    """
    Encrypts a plain text string using Fernet (AES) symmetric encryption.

    HOW FERNET WORKS INTERNALLY:
    ──────────────────────────────
    1. Fernet uses AES in CBC (Cipher Block Chaining) mode with a 128-bit key
    2. It automatically generates a random IV (Initialization Vector) each call
       → Even same message gives different ciphertext every time
    3. It signs the ciphertext with HMAC-SHA256 for data integrity
       → Any tampering is detected during decryption
    4. Final output is base64-encoded (safe to embed anywhere)

    EXAMPLE:
    ─────────
    Input:  "Hello World"
    Output: b'gAAAAABo7sjkL9d....'   (looks like garbage = secure)

    ARGS:
    ──────
    plaintext : str   → the secret message user types e.g. "Meet at 5pm"
    key       : bytes → 44-char base64 key from quantum_key.py

    RETURNS:
    ─────────
    ciphertext : bytes → encrypted unreadable token
    """

    # Create Fernet object with the quantum-generated key
    f = Fernet(key)

    # Encrypt the message
    # .encode("utf-8") converts string → bytes (Fernet needs bytes input)
    ciphertext = f.encrypt(plaintext.encode("utf-8"))

    return ciphertext
    # ciphertext is bytes like: b'gAAAAABo7sjkL9d....'


def decrypt_message(ciphertext: bytes, key: bytes) -> str:
    """
    Decrypts a Fernet ciphertext back to the original plaintext string.

    HOW DECRYPTION WORKS:
    ──────────────────────
    1. Fernet verifies the HMAC signature → confirms data was not tampered
    2. Extracts the IV from the token
    3. Decrypts using AES-CBC with the same key
    4. Returns the original bytes → decode to string

    ARGS:
    ──────
    ciphertext : bytes → the encrypted token extracted from stego image
    key        : bytes → the SAME key used during encryption (must match!)

    RETURNS:
    ─────────
    plaintext : str → original message e.g. "Meet at 5pm"

    RAISES:
    ────────
    ValueError → if key is wrong or data was tampered/corrupted
    """

    try:
        # Create Fernet object with the same key
        f = Fernet(key)

        # Decrypt: verifies HMAC → decrypts → returns bytes
        plaintext_bytes = f.decrypt(ciphertext)

        # Convert bytes → string and return
        return plaintext_bytes.decode("utf-8")

    except InvalidToken:
        # This happens when:
        # - Wrong key is used
        # - Ciphertext was modified/corrupted
        # - Image was saved as JPEG (JPEG compression destroys LSBs → corrupts ciphertext)
        raise ValueError(
            "Decryption failed! Possible reasons:\n"
            "1. Wrong Key ID used\n"
            "2. Image was saved as JPEG instead of PNG\n"
            "3. Image was edited/compressed after steganography"
        )

    except Exception as e:
        raise ValueError(f"Unexpected error during decryption: {str(e)}")
