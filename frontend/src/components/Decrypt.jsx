// ============================================================
// FILE: frontend/src/components/Decrypt.jsx
// PURPOSE: Extract hidden data from stego image and decrypt
//          Step 1: Upload stego image
//          Step 2: Enter or auto-fill Key ID
//          Step 3: Click Decrypt → see original message
// ============================================================

import React, { useState, useEffect } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

function Decrypt({ keyData }) {
  // Props:
  // keyData → shared from App.js (from Encrypt.jsx when key was generated)
  //           allows auto-filling the key_id if user stays on same session

  // ── Component State ──────────────────────────────────────────────────────

  // Selected stego image file
  const [stegoImage, setStegoImage] = useState(null);

  // Preview of stego image
  const [stegoPreview, setStegoPreview] = useState(null);

  // Key ID input (UUID from encryption step)
  const [keyId, setKeyId] = useState("");

  // The recovered plaintext message
  const [decryptedMessage, setDecryptedMessage] = useState("");

  // Status message
  const [status, setStatus] = useState("");

  // Loading state
  const [isLoading, setIsLoading] = useState(false);

  // ── Auto-fill Key ID ─────────────────────────────────────────────────────
  // When keyData is available (from Encrypt tab in same session),
  // automatically fill the key_id input to save user from copy-pasting
  useEffect(() => {
    if (keyData?.key_id) {
      setKeyId(keyData.key_id);
    }
  }, [keyData]);
  // This runs whenever keyData changes (i.e., when user generates a key)

  // ════════════════════════════════════════════════════════════════════════
  // HANDLER 1: Handle Stego Image Selection
  // ════════════════════════════════════════════════════════════════════════
  const handleImageChange = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    setStegoImage(file);
    setStegoPreview(URL.createObjectURL(file));
    setDecryptedMessage(""); // Clear previous result
    setStatus(`📁 Stego image selected: ${file.name}`);
  };

  // ════════════════════════════════════════════════════════════════════════
  // HANDLER 2: Extract and Decrypt
  // Sends stego image + key_id to POST /decrypt
  // Receives the decrypted plain text message
  // ════════════════════════════════════════════════════════════════════════
  const handleDecrypt = async () => {

    // ── Input validation ─────────────────────────────────────────────────
    if (!stegoImage) {
      setStatus("❌ Please upload the stego image first");
      return;
    }
    if (!keyId.trim()) {
      setStatus("❌ Please enter the Key ID from the encryption step");
      return;
    }

    setIsLoading(true);
    setDecryptedMessage(""); // Clear previous result
    setStatus("🔍 Extracting hidden bits from image pixels (LSB extraction)...");

    try {
      // ── Build FormData ────────────────────────────────────────────────
      const formData = new FormData();
      formData.append("image", stegoImage);     // The stego PNG file
      formData.append("key_id", keyId.trim()); // The UUID key identifier

      setStatus("🔓 Reconstructing ciphertext and decrypting with AES...");

      // ── POST to /decrypt ──────────────────────────────────────────────
      const response = await axios.post(
        `${API_URL}/decrypt`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      // response.data = { message: "Meet at airport gate B7 at 6pm" }

      // ── Display the recovered message ─────────────────────────────────
      setDecryptedMessage(response.data.message);
      setStatus("✅ Message successfully extracted and decrypted!");

    } catch (error) {
      const errMsg = error.response?.data?.detail || error.message;
      setStatus(`❌ Decryption failed: ${errMsg}`);
    }

    setIsLoading(false);
  };

  // ════════════════════════════════════════════════════════════════════════
  // RENDER
  // ════════════════════════════════════════════════════════════════════════
  return (
    <div className="panel">
      <h2>🔓 Extract & Decrypt Hidden Message</h2>

      {/* ── DECRYPTION FLOW OVERVIEW ──────────────────────────────────────── */}
      <div className="flow-overview">
        <div className="flow-step">📤 Upload Stego Image</div>
        <div className="flow-arrow">→</div>
        <div className="flow-step">🔍 Extract LSBs</div>
        <div className="flow-arrow">→</div>
        <div className="flow-step">🔢 Reconstruct Bytes</div>
        <div className="flow-arrow">→</div>
        <div className="flow-step">🔓 AES Decrypt</div>
        <div className="flow-arrow">→</div>
        <div className="flow-step">📨 Message</div>
      </div>

      {/* ── STEP 1: Upload Stego Image ────────────────────────────────────── */}
      <div className="step-card">
        <div className="step-header">
          <span className={`step-num ${stegoImage ? "step-done" : ""}`}>
            {stegoImage ? "✓" : "1"}
          </span>
          <h3>Upload Stego Image</h3>
        </div>
        <p className="step-desc">
          Upload the PNG image that contains the hidden encrypted message.
          Must be the original stego PNG — JPEG versions will NOT work
          (JPEG compression destroys the LSB hidden data).
        </p>

        <label className="file-input-label">
          📁 Choose Stego PNG
          <input
            type="file"
            accept="image/png"
            onChange={handleImageChange}
            style={{ display: "none" }}
          />
        </label>

        {stegoPreview && (
          <div className="image-preview-box">
            <p className="preview-label">Stego Image:</p>
            <img src={stegoPreview} alt="Stego" className="preview-img" />
          </div>
        )}
      </div>

      {/* ── STEP 2: Enter Key ID ──────────────────────────────────────────── */}
      <div className="step-card">
        <div className="step-header">
          <span className={`step-num ${keyId.trim() ? "step-done" : ""}`}>
            {keyId.trim() ? "✓" : "2"}
          </span>
          <h3>Enter Key ID</h3>
        </div>
        <p className="step-desc">
          Enter the Key ID you received when the quantum key was generated.
          {keyData
            ? " Auto-filled from your current session key."
            : " Paste it from the encryption step."}
        </p>

        <input
          type="text"
          className="key-input"
          placeholder="e.g. 550e8400-e29b-41d4-a716-446655440000"
          value={keyId}
          onChange={(e) => setKeyId(e.target.value)}
        />

        {/* Show auto-fill notice if key was generated in this session */}
        {keyData && (
          <p className="auto-fill-notice">
            ✅ Auto-filled from current session key
          </p>
        )}
      </div>

      {/* ── STEP 3: Decrypt ─────────────────────────────────────────────────── */}
      <div className="step-card">
        <div className="step-header">
          <span className={`step-num ${decryptedMessage ? "step-done" : ""}`}>
            {decryptedMessage ? "✓" : "3"}
          </span>
          <h3>Extract & Decrypt</h3>
        </div>
        <p className="step-desc">
          Reads the LSB of every pixel channel → reconstructs ciphertext bytes
          → finds the delimiter → decrypts with the quantum AES key.
        </p>

        <button
          className="btn btn-primary"
          onClick={handleDecrypt}
          disabled={isLoading || !stegoImage || !keyId.trim()}
        >
          {isLoading ? "⏳ Processing..." : "🔓 Extract & Decrypt Message"}
        </button>
      </div>

      {/* ── STATUS MESSAGE ─────────────────────────────────────────────────── */}
      {status && (
        <div className={`status-box ${status.startsWith("❌") ? "status-error" : status.startsWith("✅") ? "status-success" : "status-info"}`}>
          {status}
        </div>
      )}

      {/* ── RESULT: Decrypted Message ─────────────────────────────────────── */}
      {decryptedMessage && (
        <div className="result-box">
          <h3>📨 Decrypted Secret Message</h3>
          <div className="decrypted-message">
            {decryptedMessage}
          </div>
          <p className="result-meta">
            Length: {decryptedMessage.length} characters &nbsp;|&nbsp; Encoding: UTF-8
          </p>
        </div>
      )}
      

    </div>
  );
}

export default Decrypt;
