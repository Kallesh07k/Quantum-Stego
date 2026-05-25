# Quantum-Inspired Secure Image Steganography Platform
## Complete Setup & Run Guide

---

## PROJECT STRUCTURE

```
QuantumProject/
│
├── backend/
│   ├── main.py                   ← FastAPI server (run this)
│   ├── requirements.txt          ← pip install list
│   ├── uploads/                  ← temp image folder (auto-created)
│   │
│   ├── quantum/
│   │   ├── __init__.py
│   │   └── quantum_key.py        ← Qiskit 256-qubit key generator
│   │
│   ├── encryption/
│   │   ├── __init__.py
│   │   └── aes_encrypt.py        ← Fernet AES encrypt/decrypt
│   │
│   └── steganography/
│       ├── __init__.py
│       └── stego.py              ← LSB hide/extract
│
└── frontend/
    ├── index.html                ← HTML shell
    ├── package.json              ← npm dependencies
    ├── vite.config.js            ← Vite config
    └── src/
        ├── main.jsx              ← React entry point
        ├── App.js                ← Root component + tab nav
        ├── App.css               ← All styles
        └── components/
            ├── Encrypt.jsx       ← Encrypt & Hide panel
            └── Decrypt.jsx       ← Extract & Decrypt panel
```

---

## STEP 1 — SET UP BACKEND

```bash
# Navigate to backend folder
cd QuantumProject/backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Create uploads folder (if not exists)
mkdir uploads

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

Test it works: Open http://127.0.0.1:8000 → should see {"status": "ok", ...}
API docs:     Open http://127.0.0.1:8000/docs → Swagger UI

---

## STEP 2 — SET UP FRONTEND

Open a NEW terminal (keep backend running in the first one):

```bash
# Navigate to frontend folder
cd QuantumProject/frontend

# Install Node.js packages
npm install

# Start the React dev server
npm run dev
```

You should see:
```
VITE v5.x  ready in 300ms
➜  Local:   http://localhost:5173/
```

Open http://localhost:5173 in your browser.

---

## STEP 3 — USE THE APP

### Encrypting a message:
1. Click "⚛ Generate Quantum Key" → wait for Qiskit to run (~5-15 seconds)
2. Note the Key ID displayed (save it!)
3. Click "📁 Choose Image" → select any PNG/JPG image
4. Type your secret message in the textarea
5. Click "🔐 Encrypt & Hide Message"
6. Download the stego PNG image

### Decrypting a message:
1. Switch to "🔓 Extract & Decrypt" tab
2. Upload the stego PNG image
3. Paste the Key ID (auto-filled if same session)
4. Click "🔓 Extract & Decrypt Message"
5. See the original secret message

---

## TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: qiskit` | Run `pip install qiskit qiskit-aer` |
| `Cannot read image` | Check file path, try a different image format |
| `Delimiter not found` | Image was saved as JPEG — must use PNG |
| `Invalid key_id` | Server restarted — generate a new key |
| CORS error in browser | Make sure backend is on port 8000, frontend on 5173 |
| `npm: command not found` | Install Node.js from https://nodejs.org |
| Qiskit takes too long | Normal — simulating 256 qubits takes 5-20 seconds |
| Image too small error | Use a larger image (512×512 or bigger) |

---

## API ENDPOINTS

| Method | URL | Purpose |
|--------|-----|---------|
| GET | /generate-key | Run quantum circuit, return key_id |
| POST | /encrypt | Hide encrypted message in image |
| POST | /decrypt | Extract and decrypt hidden message |
| GET | / | Health check |
| GET | /docs | Swagger UI (auto-generated) |

---

## HOW THE SECURITY WORKS

```
Secret message: "Meet at gate B7"
        ↓
[AES Fernet encrypt with quantum key]
        ↓
Ciphertext: "gAAAAABo7sjkL9d..." (unreadable)
        ↓
[Convert to binary: 01001000...]
        ↓
[LSB embed into image pixels]
        ↓
Stego image (visually identical, contains hidden encrypted data)
```

Attacker gets the image → sees a normal photo → no idea anything is hidden.
Even if they suspect steganography → ciphertext is still AES encrypted.
= Dual layer security.
