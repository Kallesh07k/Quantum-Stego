# ============================================================
# FILE: backend/steganography/stego.py
# PURPOSE: Hide encrypted bytes inside image pixels using LSB
#          and extract them back out
# ============================================================

import cv2      # OpenCV: for reading, writing, and manipulating image pixels
import numpy as np  # NumPy: for efficient array operations on pixel data

# ── WHAT IS LSB STEGANOGRAPHY? ──────────────────────────────────────────────
#
# Every image pixel has 3 channels: Red, Green, Blue
# Each channel is 1 byte (0-255), stored as 8 bits
#
# Example pixel:
#   R = 182 = 10110110
#   G = 200 = 11001000
#   B = 140 = 10001100
#
# The LAST BIT (Least Significant Bit) barely affects the color:
#   182 (10110110) vs 183 (10110111) → difference of 1 → invisible to human eye
#
# So we replace that last bit with 1 bit of secret data.
#
# Capacity:
#   A 512×512 image = 512 × 512 × 3 channels = 786,432 bits = 98,304 bytes
#   More than enough for typical messages
# ────────────────────────────────────────────────────────────────────────────

# Delimiter = unique sequence appended to data so we know where it ends
# Must be something unlikely to appear naturally in ciphertext
DELIMITER = "<<QUANTUM_STEGO_END>>"


def bytes_to_binary(data: bytes) -> str:
    """
    Converts bytes into a string of 0s and 1s (binary representation).

    EXAMPLE:
    ─────────
    data = b'Hi'
    → 'H' = 72  = 01001000
    → 'i' = 105 = 01101001
    → result: '0100100001101001'

    format(byte, '08b') means:
    - Convert byte value to binary
    - Pad with leading zeros to always get 8 digits
    """
    binary_string = ""
    for byte in data:
        binary_string += format(byte, "08b")  # e.g., 72 → '01001000'
    return binary_string


def binary_to_bytes(binary_str: str) -> bytes:
    """
    Converts a string of 0s and 1s back into bytes.

    EXAMPLE:
    ─────────
    '0100100001101001' → b'Hi'

    We take 8 bits at a time, convert to integer, then to byte.
    """
    result = bytearray()
    # Process 8 bits at a time (1 byte at a time)
    for i in range(0, len(binary_str) - 7, 8):
        chunk = binary_str[i : i + 8]          # Take 8 bits
        byte_val = int(chunk, 2)                # '01001000' → 72
        result.append(byte_val)                 # Add to result
    return bytes(result)


def hide_data(image_path: str, ciphertext: bytes, output_path: str) -> None:
    """
    Hides the encrypted ciphertext inside an image using LSB steganography.
    Saves the result as a PNG (lossless — NEVER use JPEG, it destroys the LSBs).

    HOW IT WORKS STEP BY STEP:
    ────────────────────────────
    1. Load image using OpenCV → get pixel array of shape (H, W, 3)
    2. Add DELIMITER to the end of ciphertext so extraction knows where to stop
    3. Convert everything to binary: b'gAAAA...' → '010101110101...'
    4. Flatten image to 1D array: [182, 200, 140, 178, ...] (channel values)
    5. For each bit of secret data:
         - Take the channel value
         - Clear its last bit:   value & 0b11111110  (AND with 254)
         - Set last bit to data: result | bit         (OR with 0 or 1)
    6. Reshape array back to image dimensions
    7. Save as PNG (lossless — PNG preserves exact pixel values)

    EXAMPLE LSB EMBEDDING:
    ───────────────────────
    channel value = 182 = 10110110
    we want to hide bit = 1
    step a: clear LSB → 182 & 254 = 182 & 11111110 = 10110110 = 182
    step b: set LSB   → 182 | 1   = 182 | 00000001 = 10110111 = 183
    result: 183. Visually identical to 182.

    we want to hide bit = 0
    step a: clear LSB → 182 & 254 = 182
    step b: set LSB   → 182 | 0   = 182
    result: 182 unchanged.

    ARGS:
    ──────
    image_path  : str   → path to the original cover image
    ciphertext  : bytes → encrypted message bytes from Fernet
    output_path : str   → where to save the stego PNG

    RAISES:
    ────────
    ValueError → if image cannot be read or is too small for the data
    """

    # ── Load the image ────────────────────────────────────────────────────
    image = cv2.imread(image_path)
    # image is a NumPy array of shape (height, width, 3)
    # Each element is a uint8 (0-255) representing R, G, or B value

    if image is None:
        raise ValueError(f"Could not open image at: {image_path}")

    # ── Prepare the full payload ───────────────────────────────────────────
    # We append the DELIMITER so the extractor knows where data ends
    delimiter_bytes = DELIMITER.encode("utf-8")
    full_payload = ciphertext + delimiter_bytes
    # Example: b'gAAAAABo...' + b'<<QUANTUM_STEGO_END>>'

    # ── Convert payload to binary string ─────────────────────────────────
    binary_payload = bytes_to_binary(full_payload)
    # binary_payload = '01001000...' (very long string of 0s and 1s)

    total_bits = len(binary_payload)

    # ── Check image has enough capacity ───────────────────────────────────
    # Flatten shape (H, W, 3) → 1D array
    # Total channels = H × W × 3 = maximum bits we can hide
    flat = image.flatten()
    capacity = len(flat)  # number of individual channel values = number of bits we can hide

    if total_bits > capacity:
        raise ValueError(
            f"Image too small!\n"
            f"Image capacity: {capacity} bits ({capacity // 8} bytes)\n"
            f"Data needed:    {total_bits} bits ({total_bits // 8} bytes)\n"
            f"Please use a larger image."
        )

    # ── Embed each bit into the LSB of each channel value ─────────────────
    for i in range(total_bits):
        bit = int(binary_payload[i])       # Get next bit (0 or 1) as integer

        # Clear the last bit of the pixel channel value
        # 0b11111110 = 254 in decimal
        # Example: 10110110 & 11111110 = 10110110 (last bit cleared to 0)
        cleared = int(flat[i]) & 0b11111110

        # Set the last bit to our data bit
        # If bit=1: 10110110 | 1 = 10110111
        # If bit=0: 10110110 | 0 = 10110110
        flat[i] = cleared | bit

    # ── Reshape back to original image dimensions ──────────────────────────
    stego_image = flat.reshape(image.shape)

    # ── Save as PNG (CRITICAL: never JPEG — JPEG compresses and destroys LSBs)
    success = cv2.imwrite(output_path, stego_image)
    if not success:
        raise RuntimeError(f"Failed to save stego image to: {output_path}")

    print(f"[stego.py] Successfully embedded {total_bits} bits into image.")
    print(f"[stego.py] Used {round(total_bits/capacity*100, 2)}% of image capacity.")


def extract_data(stego_image_path: str) -> bytes:
    """
    Extracts and returns the hidden ciphertext from a stego image.

    HOW EXTRACTION WORKS:
    ──────────────────────
    1. Load stego image
    2. Flatten pixel array to 1D
    3. Read the LAST BIT of each channel value → collect all LSBs
    4. Build a long string of 0s and 1s
    5. Convert back to bytes
    6. Search for the DELIMITER → marks the end of hidden data
    7. Return everything BEFORE the delimiter = ciphertext

    ARGS:
    ──────
    stego_image_path : str → path to the stego PNG image

    RETURNS:
    ─────────
    ciphertext : bytes → encrypted data ready for Fernet decryption

    RAISES:
    ────────
    ValueError → if image cannot be read or delimiter not found
    """

    # ── Load the stego image ───────────────────────────────────────────────
    image = cv2.imread(stego_image_path)

    if image is None:
        raise ValueError(f"Could not open image at: {stego_image_path}")

    # ── Flatten to 1D array ───────────────────────────────────────────────
    flat = image.flatten()

    # ── Extract LSB from every channel value ─────────────────────────────
    # value & 1 isolates the last bit
    # Example: 10110111 & 00000001 = 00000001 = 1
    # Example: 10110110 & 00000001 = 00000000 = 0
    bits = ""
    for val in flat:
        bits += str(int(val) & 1)
    # bits is now a long string like '10110100110...'

    # ── Convert binary string back to bytes ─────────────────────────────
    all_bytes = binary_to_bytes(bits)

    # ── Search for the DELIMITER ──────────────────────────────────────────
    delimiter_bytes = DELIMITER.encode("utf-8")
    delimiter_pos = all_bytes.find(delimiter_bytes)

    if delimiter_pos == -1:
        raise ValueError(
            "No hidden data found in this image!\n"
            "Possible reasons:\n"
            "1. This image was never used for steganography\n"
            "2. Image was converted to JPEG (destroys hidden data)\n"
            "3. Image was edited after steganography"
        )

    # Everything before the delimiter is the ciphertext
    ciphertext = all_bytes[:delimiter_pos]

    print(f"[stego.py] Extracted {len(ciphertext)} bytes of ciphertext.")
    return ciphertext
