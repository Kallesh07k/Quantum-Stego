// ============================================================
// FILE: frontend/src/components/Encrypt.jsx
// PURPOSE: Full encrypt + hide workflow
//          Step 1: Generate quantum key
//          Step 2: Upload cover image
//          Step 3: Enter secret message
//          Step 4: Click Encrypt → download stego image
// ============================================================

import React, { useState } from "react";
import axios from "axios";
// axios → HTTP client library to send requests to the FastAPI backend

// The FastAPI backend URL
// Make sure backend is running on this address before using the app
const API_URL = "https://quantum-stego-wk2f.onrender.com";
function Encrypt({ keyData, setKeyData }) {
  // Props:
  // keyData    → current quantum key info (null if not generated yet)
  // setKeyData → function to update keyData in App.js (shared with Decrypt)

  // ── Component State ──────────────────────────────────────────────────────

  // Selected cover image file object (from file input)
  const [image, setImage] = useState(null);

  // Preview URL for showing the selected image in the browser
  const [imagePreview, setImagePreview] = useState(null);

  // Secret message typed by user
  const [message, setMessage] = useState("");

  // Status message to show user (loading, error, success)
  const [status, setStatus] = useState("");

  // Whether the app is currently loading (disable buttons during API calls)
  const [isLoading, setIsLoading] = useState(false);

  // URL of the generated stego image (for download link + preview)
  const [stegoImageUrl, setStegoImageUrl] = useState(null);

  // ════════════════════════════════════════════════════════════════════════
  // HANDLER 1: Generate Quantum Key
  // Calls GET /generate-key → gets key_id and quantum bits
  // ════════════════════════════════════════════════════════════════════════
  const handleGenerateKey = async () => {
    setIsLoading(true);
    setStatus("⚛ Running Qiskit quantum circuit... (256 qubits, Hadamard gates)");
    setStegoImageUrl(null); // Reset stego image if regenerating key

    try {
      // GET request to backend /generate-key endpoint
      const response = await axios.get(`${API_URL}/generate-key`);
      // response.data = {
      //   key_id: "550e8400-...",
      //   quantum_bits: [1,0,1,1,...],
      //   message: "Quantum key generated successfully"
      // }

      // Save key data to App.js state (shared with Decrypt component)
      setKeyData(response.data);

      setStatus(
        `✅ Quantum key generated! Key ID: ${response.data.key_id.slice(0, 16)}...`
        // Show first 16 chars of key_id to confirm generation
      );

    } catch (error) {
      // Show error if backend is not running or Qiskit fails
      const errMsg = error.response?.data?.detail || error.message;
      setStatus(`❌ Key generation failed: ${errMsg}`);
    }

    setIsLoading(false);
  };

  // ════════════════════════════════════════════════════════════════════════
  // HANDLER 2: Handle Image File Selection
  // Called when user selects an image file from file input
  // ════════════════════════════════════════════════════════════════════════
  const handleImageChange = (e) => {
    const file = e.target.files[0]; // Get the selected file

    if (!file) return; // User cancelled file dialog

    setImage(file); // Store the File object for sending to backend

    // Create a local URL for preview (doesn't upload anything yet)
    // URL.createObjectURL() creates a temporary in-memory URL
    const previewUrl = URL.createObjectURL(file);
    setImagePreview(previewUrl);

    setStegoImageUrl(null); // Reset previous stego result
    setStatus(`📁 Image selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`);
  };

  // ════════════════════════════════════════════════════════════════════════
  // HANDLER 3: Encrypt and Hide
  // Sends image + message + key_id to POST /encrypt
  // Receives stego image PNG as binary response
  // ════════════════════════════════════════════════════════════════════════
  const handleEncrypt = async () => {

    // ── Input validation ─────────────────────────────────────────────────
    if (!keyData) {
      setStatus("❌ Please generate a quantum key first (Step 1)");
      return;
    }
    if (!image) {
      setStatus("❌ Please select a cover image (Step 2)");
      return;
    }
    if (!message.trim()) {
      setStatus("❌ Please enter a secret message (Step 3)");
      return;
    }

    setIsLoading(true);
    setStatus("🔐 Encrypting message with AES Fernet...");

    try {
      // ── Build FormData ────────────────────────────────────────────────
      // FormData is used for multipart/form-data requests
      // (required for file + text fields in the same request)
      const formData = new FormData();
      formData.append("image", image);           // File object
      formData.append("message", message);       // String
      formData.append("key_id", keyData.key_id); // String (UUID)

      setStatus("🖼 Hiding encrypted data in image pixels (LSB)...");

      // ── Send POST request to /encrypt ─────────────────────────────────
      const response = await axios.post(
        `${API_URL}/encrypt`,
        formData,
        {
          responseType: "blob",
          // responseType: "blob" → tells axios to receive binary data (the PNG image)
          // Without this, axios tries to parse the response as JSON (which fails for images)

          headers: {
            "Content-Type": "multipart/form-data",
            // Tell server this is a form-data request with file
          },
        }
      );

      // ── Create a downloadable URL from the PNG blob ───────────────────
      // response.data is a Blob (binary data of the PNG file)
      const blob = new Blob([response.data], { type: "image/png" });
      const url = URL.createObjectURL(blob);
      // url is a temporary browser URL like "blob:http://localhost:5173/abc123"

      setStegoImageUrl(url);
      setStatus("✅ Done! Your stego image is ready. Download it below.");

    } catch (error) {
      const errMsg = error.response?.data?.detail || error.message;
      setStatus(`❌ Encryption failed: ${errMsg}`);
    }

    setIsLoading(false);
  };

  // ════════════════════════════════════════════════════════════════════════
  // RENDER
  // ════════════════════════════════════════════════════════════════════════
  return (
    <div className="panel">
      <h2>🔐 Encrypt & Hide Secret Message</h2>

      {/* ── STEP 1: Generate Quantum Key ──────────────────────────────────── */}
      <div className="step-card">
        <div className="step-header">
          <span className={`step-num ${keyData ? "step-done" : ""}`}>
            {keyData ? "✓" : "1"}
          </span>
          <h3>Generate Quantum Key</h3>
        </div>
        <p className="step-desc">
          Uses Qiskit to run a 256-qubit quantum circuit. Each qubit enters
          superposition via Hadamard gate, then collapses to a random 0 or 1 on
          measurement. The 256 bits form your AES encryption key.
        </p>

        <button
          className="btn btn-primary"
          onClick={handleGenerateKey}
          disabled={isLoading}
        >
          {isLoading && !keyData ? "⏳ Generating..." : keyData ? "⚛ Regenerate Key" : "⚛ Generate Quantum Key"}
        </button>

        {/* Show key info after generation */}
        {keyData && (
          <div className="key-info">
            <p><strong>Key ID:</strong> <code>{keyData.key_id}</code></p>
            <p className="warning-text">
              Save this Key ID — you need it to decrypt the message later!
            </p>
            {/* Quantum bits visualization */}
            <div className="bits-label">Quantum measurement output (first 64 bits):</div>
            <div className="bits-display">
              {keyData.quantum_bits.map((bit, index) => (
                <span
                  key={index}
                  className={`bit ${bit === 1 ? "bit-one" : "bit-zero"}`}
                >
                  {bit}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ── STEP 2: Upload Cover Image ────────────────────────────────────── */}
      <div className="step-card">
        <div className="step-header">
          <span className={`step-num ${image ? "step-done" : ""}`}>
            {image ? "✓" : "2"}
          </span>
          <h3>Upload Cover Image</h3>
        </div>
        <p className="step-desc">
          Select a PNG or JPG image to hide data inside. The stego image will
          always be saved as PNG (lossless). Larger image = more capacity.
          A 512×512 image can hold ~96 KB of hidden data.
        </p>

        <label className="file-input-label">
          📁 Choose Image
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            style={{ display: "none" }}
          />
        </label>

        {/* Image preview after selection */}
        {imagePreview && (
          <div className="image-preview-box">
            <p className="preview-label">Cover Image:</p>
            <img src={imagePreview} alt="Cover" className="preview-img" />
          </div>
        )}
      </div>

      {/* ── STEP 3: Enter Secret Message ──────────────────────────────────── */}
      <div className="step-card">
        <div className="step-header">
          <span className={`step-num ${message.trim() ? "step-done" : ""}`}>
            {message.trim() ? "✓" : "3"}
          </span>
          <h3>Enter Secret Message</h3>
        </div>
        <p className="step-desc">
          Type the confidential message to encrypt and hide inside the image.
        </p>

        <textarea
          className="message-textarea"
          placeholder="Type your secret message here...&#10;Example: Meet at airport gate B7 at 6pm"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={4}
        />
        {message && (
          <p className="char-count">
            {message.length} characters → ~{message.length * 8} bits needed
          </p>
        )}
      </div>

      {/* ── STEP 4: Encrypt & Hide ─────────────────────────────────────────── */}
      <div className="step-card">
        <div className="step-header">
          <span className={`step-num ${stegoImageUrl ? "step-done" : ""}`}>
            {stegoImageUrl ? "✓" : "4"}
          </span>
          <h3>Encrypt & Hide</h3>
        </div>
        <p className="step-desc">
          Encrypts the message with AES Fernet using the quantum key,
          then hides the ciphertext in image pixels by modifying the
          Least Significant Bit of each RGB channel.
        </p>

        <button
          className="btn btn-success"
          onClick={handleEncrypt}
          disabled={isLoading || !keyData || !image || !message.trim()}
        >
          {isLoading ? "⏳ Processing..." : "🔐 Encrypt & Hide Message"}
        </button>
      </div>

      {/* ── STATUS MESSAGE ─────────────────────────────────────────────────── */}
      {status && (
        <div className={`status-box ${status.startsWith("❌") ? "status-error" : status.startsWith("✅") ? "status-success" : "status-info"}`}>
          {status}
        </div>
      )}

      {/* ── RESULT: Stego Image Download ──────────────────────────────────── */}
      {stegoImageUrl && (
        <div className="result-box">
          <h3>✅ Stego Image Ready</h3>
          <p>
            This image looks identical to the original but contains your
            encrypted message hidden in the pixel LSBs.
          </p>

          {/* Side-by-side comparison */}
          <div className="comparison">
            <div className="comparison-item">
              <p className="comparison-label">Original</p>
              <img src={imagePreview} alt="Original" className="result-img" />
            </div>
            <div className="comparison-divider">VS</div>
            <div className="comparison-item">
              <p className="comparison-label">Stego (has hidden data)</p>
              <img src={stegoImageUrl} alt="Stego" className="result-img" />
            </div>
          </div>

          {/* Download button */}
          <a
            href={stegoImageUrl}
            download={`qstego_${Date.now()}_${Math.random().toString(16).slice(2,7)}.png`}
            className="btn btn-download"
          >
            ⬇ Download Stego Image
          </a>
        </div>
      )}

    </div>
  );
}

export default Encrypt;