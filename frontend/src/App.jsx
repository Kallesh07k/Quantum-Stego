// ============================================================
// FILE: frontend/src/App.js
// PURPOSE: Root component — renders header + tab navigation
//          + switches between Encrypt and Decrypt panels
// ============================================================

import React, { useState } from "react";
// useState → React hook to manage component state (which tab is active, shared key data)

import Encrypt from "./components/Encrypt";
// Encrypt component → shows the encrypt + hide workflow

import Decrypt from "./components/Decrypt";
// Decrypt component → shows the extract + decrypt workflow

import "./App.css";
// Global CSS styles for the whole application

function App() {
  // ── State: which tab is currently active ────────────────────────────────
  // activeTab = "encrypt" OR "decrypt"
  const [activeTab, setActiveTab] = useState("encrypt");
  // Initially show the encrypt tab

  // ── State: shared key data between Encrypt and Decrypt ──────────────────
  // keyData is set by Encrypt.jsx when the user generates a quantum key
  // keyData = { key_id: "550e8400-...", quantum_bits: [1,0,1,...] }
  // Decrypt.jsx can read it to auto-fill the key_id field
  const [keyData, setKeyData] = useState(null);
  // null = no key generated yet

  return (
    <div className="app-container">

      {/* ── HEADER ──────────────────────────────────────────────────────── */}
      <header className="app-header">
        <h1>⚛ Quantum Stego</h1>
        <p>Quantum-Inspired Secure Image Steganography Platform</p>

        {/* Technology badges */}
        <div className="tech-badges">
          <span className="badge">Qiskit</span>
          <span className="badge">AES Fernet</span>
          <span className="badge">LSB Steganography</span>
          <span className="badge">FastAPI</span>
          <span className="badge">React</span>
        </div>
      </header>

      {/* ── TAB NAVIGATION ────────────────────────────────────────────────── */}
      {/* Two tabs: Encrypt & Hide | Extract & Decrypt */}
      <nav className="tab-nav">
        {/* Encrypt tab button */}
        <button
          className={`tab-btn ${activeTab === "encrypt" ? "tab-active" : ""}`}
          onClick={() => setActiveTab("encrypt")}
        >
          🔐 Encrypt & Hide
        </button>

        {/* Decrypt tab button */}
        <button
          className={`tab-btn ${activeTab === "decrypt" ? "tab-active" : ""}`}
          onClick={() => setActiveTab("decrypt")}
        >
          🔓 Extract & Decrypt
        </button>
      </nav>

      {/* ── MAIN CONTENT AREA ─────────────────────────────────────────────── */}
      <main className="main-content">

        {/* Render Encrypt component when encrypt tab is active */}
        {activeTab === "encrypt" && (
          <Encrypt
            keyData={keyData}
            setKeyData={setKeyData}
            // setKeyData allows Encrypt.jsx to update keyData in App.js
            // which can then be passed to Decrypt.jsx
          />
        )}

        {/* Render Decrypt component when decrypt tab is active */}
        {activeTab === "decrypt" && (
          <Decrypt keyData={keyData} />
          // Pass keyData so Decrypt.jsx can auto-fill the key_id input
        )}

      </main>

      {/* ── FOOTER ─────────────────────────────────────────────────────────── */}
      <footer className="app-footer">
        <p>
          Dual-layer security: AES Encryption + LSB Steganography + Quantum Key Generation
        </p>
      </footer>

    </div>
  );
}

export default App;
