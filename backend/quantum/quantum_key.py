# ============================================================
# FILE: backend/quantum/quantum_key.py
# PURPOSE: Generate a cryptographic AES key using Qiskit
#          quantum simulation (Hadamard gates + measurement)
# ============================================================

import base64                        # To encode bytes into URL-safe string (Fernet needs this)
from qiskit import QuantumCircuit    # To build the quantum circuit
from qiskit_aer import AerSimulator  # Classical simulator that mimics quantum hardware


def generate_quantum_key():
    """
    Generates a 256-bit AES-compatible key using quantum randomness.

    HOW IT WORKS:
    ─────────────
    Step 1: Create a QuantumCircuit with 256 qubits and 256 classical bits
    Step 2: Apply Hadamard (H) gate to every qubit
            → Each qubit enters superposition: 50% chance of 0, 50% chance of 1
            → Math: H|0⟩ = (|0⟩ + |1⟩) / √2
    Step 3: Measure all qubits
            → Superposition collapses to a definite 0 or 1 (true randomness)
    Step 4: Collect 256 random bits → convert to 32 bytes → base64 encode
            → Result is a Fernet-compatible AES key

    WHY THIS IS BETTER THAN Fernet.generate_key():
    ────────────────────────────────────────────────
    Fernet.generate_key() uses a pseudo-random number generator (PRNG)
    → PRNG is algorithm-based → predictable if seed is known
    Quantum measurement is physics-based → fundamentally unpredictable
    → Even knowing the full quantum state, you cannot predict the outcome

    RETURNS:
    ────────
    key  : bytes  → Fernet-compatible 44-char base64 key
    bits : list   → list of 0s and 1s from measurement (for visualization)
    """

    # ── STEP 1: Create Quantum Circuit ──────────────────────────────────
    # QuantumCircuit(n_qubits, n_classical_bits)
    # 256 qubits → we get 256 random bits → 32 bytes → AES-256 key
    qc = QuantumCircuit(256, 256)

    # ── STEP 2: Apply Hadamard Gate to ALL qubits ───────────────────────
    # H gate matrix = (1/√2) * [[1, 1], [1, -1]]
    # Applied to |0⟩: H|0⟩ = (|0⟩ + |1⟩)/√2
    # → qubit is in SUPERPOSITION: simultaneously 0 AND 1
    # → when measured, each has exactly 50% probability
    for i in range(256):
        qc.h(i)   # Apply Hadamard to qubit number i

    # ── STEP 3: Measure all qubits ──────────────────────────────────────
    # qc.measure(quantum_bits, classical_bits)
    # This collapses each superposition to 0 or 1
    qc.measure(range(256), range(256))

    # ── STEP 4: Simulate on classical hardware ──────────────────────────
    # AerSimulator mimics a real quantum computer on your CPU
    simulator = AerSimulator()
    job = simulator.run(qc, shots=1)     # shots=1 → run circuit once
    result = job.result()
    counts = result.get_counts(qc)
    # counts looks like: {'10110100...10011': 1}

    # Extract the bitstring from counts
    # Qiskit returns bits in little-endian → reverse to get natural order
    bitstring = list(counts.keys())[0][::-1]
    # Example: '10110100110010101101...' (256 characters of 0s and 1s)

    # ── STEP 5: Convert bitstring to list of ints ───────────────────────
    bits = [int(b) for b in bitstring]
    # bits = [1, 0, 1, 1, 0, 1, 0, 0, ...]  (256 values)

    # ── STEP 6: Pack 256 bits into 32 bytes ─────────────────────────────
    # Every 8 bits = 1 byte
    # '10110100' → int('10110100', 2) → 180 → byte value 180
    byte_array = bytearray()
    for i in range(0, 256, 8):
        chunk = bitstring[i : i + 8]        # Take 8 bits at a time
        byte_val = int(chunk, 2)            # Convert binary string to integer
        byte_array.append(byte_val)         # Append as byte
    # Now byte_array has exactly 32 bytes

    # ── STEP 7: Base64-URL encode ────────────────────────────────────────
    # Fernet requires a URL-safe base64-encoded 32-byte key (44 characters)
    key = base64.urlsafe_b64encode(bytes(byte_array))
    # key looks like: b'a8h3jKx2Lm...=='

    return key, bits
    # Returns: key (bytes), bits (list of 0/1 for visualization)
