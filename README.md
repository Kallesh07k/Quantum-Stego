<div align="center">

# ⚛️ Quantum-Stego

### Securely hide encrypted messages inside images

[![Live Demo](https://img.shields.io/badge/Live_Demo-Visit_App-blue?style=for-the-badge)](https://quantum-stego-mu.vercel.app)
[![API Docs](https://img.shields.io/badge/API_Docs-Swagger_UI-orange?style=for-the-badge)](https://quantum-stego-wk2f.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)

</div>

---

## 📌 Overview

**Quantum-Stego** is a full-stack web application that combines **Quantum-Inspired Key Generation**, **AES Encryption**, and **LSB Image Steganography** to create a dual-layer secure communication system.

A secret message is encrypted using a quantum-generated key, then invisibly embedded into a PNG image. The resulting stego image looks completely normal — with no visible trace of hidden data. Even if steganography is suspected, the message remains AES-encrypted without the Key ID.

```
Secret Message
      ↓
Quantum Key Generation (Qiskit)
      ↓
AES Fernet Encryption → Ciphertext
      ↓
LSB Embed into Image Pixels
      ↓
Stego Image (visually identical to original)
```

---

## ✅ Features

- ⚛️ Quantum-inspired key generation using Qiskit simulation
- 🔐 AES Fernet encryption for secure message protection
- 🖼️ LSB steganography — hides data invisibly in image pixels
- 🔓 Full extraction and decryption workflow
- ⚡ FastAPI backend with Swagger documentation
- 🌐 React frontend deployed on Vercel
- ☁️ Fully cloud-deployed and accessible from any device

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, Vite, Axios |
| Backend | FastAPI, Python, Uvicorn |
| Quantum Key | Qiskit, Qiskit AerSimulator |
| Encryption | Cryptography — Fernet (AES) |
| Image Processing | OpenCV, NumPy, Pillow |
| Deployment | Vercel (frontend), Render (backend) |

---

## 📁 Project Structure

```
Quantum-Stego/
├── backend/
│   ├── main.py                  ← FastAPI routes
│   ├── requirements.txt
│   ├── quantum/
│   │   └── quantum_key.py       ← Qiskit key generator
│   ├── encryption/
│   │   └── aes_encrypt.py       ← AES encrypt / decrypt
│   └── steganography/
│       └── stego.py             ← LSB hide / extract
│
└── frontend/
    ├── src/
    │   ├── App.js
    │   └── components/
    │       ├── Encrypt.jsx       ← Encrypt & Hide panel
    │       └── Decrypt.jsx       ← Extract & Decrypt panel
    └── package.json
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.9+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv venv

# Activate — Windows:
venv\Scripts\activate
# Activate — macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend runs at: http://127.0.0.1:8000  
Swagger docs at: http://127.0.0.1:8000/docs

### Frontend

Open a **new terminal:**

```bash
cd frontend
npm install
npm run dev
```

App runs at: http://localhost:5173

---

## 📖 How to Use

### 🔐 Encrypt a Message
1. Click **Generate Quantum Key** — wait 5–15 seconds for Qiskit to run
2. **Save the Key ID** shown — you'll need it to decrypt
3. Upload a PNG image (512×512 px or larger)
4. Type your secret message and click **Encrypt & Hide**
5. Download the stego image

### 🔓 Decrypt a Message
1. Switch to the **Extract & Decrypt** tab
2. Upload the stego image and enter the Key ID
3. Click **Extract & Decrypt** to reveal the original message

> ⚠️ **PNG only** — JPEG compression destroys the hidden LSB data.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/generate-key` | Generate quantum key → returns `key_id` |
| POST | `/encrypt` | Encrypt message and embed into image |
| POST | `/decrypt` | Extract and decrypt hidden message |
| GET | `/docs` | Swagger UI |

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: qiskit` | `pip install qiskit qiskit-aer` |
| `Delimiter not found` | Use PNG — not JPEG |
| `Invalid key_id` | Server restarted — generate a new key |
| Qiskit is slow | Normal — quantum simulation takes 5–20 sec |
| Image too small | Use an image at least 512×512 px |
| Backend cold start | Render free tier — wait 30–60 sec on first request |

---

## 🔮 Future Enhancements

- Real quantum hardware via IBM Quantum Network
- JWT authentication and user accounts
- Database storage for keys and message history
- Video and audio steganography support
- Mobile app (React Native)

---
