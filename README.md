# 🔐 HMAC Client-Server Communication System

---

## 📋 Përshkrimi

Ky projekt implementon një sistem të sigurt komunikimi klient-server duke përdorur **HMAC-SHA256** (Hash-based Message Authentication Code) për të garantuar **integritetin** dhe **autenticitetin** e mesazheve të shkëmbyera mbi rrjet.

Sistemi përbëhet nga dy komponentë:

| Komponenti | Roli |
|---|---|
| `server.py` | Pret lidhje TCP, merr mesazhe, verifikon HMAC-in dhe kthen përgjigje |
| `client.py` | Merr input nga përdoruesi, gjeneron HMAC, dërgon payload JSON te serveri |

---

## 🏗️ Arkitektura

```
┌─────────────────────────────────────────────────────────┐
│                        CLIENT                           │
│                                                         │
│  Përdoruesi shtype mesazh                               │
│        │                                                │
│        ▼                                                │
│  generate_hmac(message)  ←  SECRET_KEY                  │
│        │                                                │
│        ▼                                                │
│  {"message": "...", "hmac": "..."}  ──TCP──►  SERVER    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                        SERVER                           │
│                                                         │
│  Merr payload JSON                                      │
│        │                                                │
│        ▼                                                │
│  verify_hmac(message, received_hmac)  ←  SECRET_KEY     │
│        │                                                │
│        ▼                                                │
│  ✅ "Message verified"  ──TCP──►  CLIENT                │
│  ❌ "Verification failed"                               │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Kërkesat

- **Python 3.10+** (për shkak të sintaksës `str | None`)
- Asnjë librari e jashtme — vetëm modulet standarde:

```
socket    hmac    hashlib    json    logging    os
```

---

## 🚀 Si të ekzekutohet

### Hapi 1 — Vendos çelësin sekret

Hap **dy terminale** dhe ekzekuto në secilin:

**Windows PowerShell:**
```powershell
$env:HMAC_SECRET="fjalekalimi_im_secret"
```

**Linux / macOS:**
```bash
export HMAC_SECRET="fjalekalimi_im_secret"
```

> ⚠️ **E rëndësishme:** Çelësi duhet të jetë **identik** në të dy terminalet. Nëse ndryshon edhe një shkronjë, verifikimi do të dështojë.

---

### Hapi 2 — Starto serverin (Terminal 1)

```bash
python server.py
```

**Output i pritur:**
```
Server started and awaiting messages...
2026-05-04 12:00:00 - SERVER - INFO - Server listening on 127.0.0.1:65432
```

---

### Hapi 3 — Starto klientin (Terminal 2)

```bash
python client.py
```

**Output i pritur:**
```
2026-05-04 12:00:05 - CLIENT - INFO - Connected to server 127.0.0.1:65432

Enter your message (or 'exit' to quit):
```

---

### Hapi 4 — Dërgo mesazhe

Shkruaj çdo mesazh dhe shtyp **Enter**:

```
Enter your message (or 'exit' to quit): Ky është një mesazh i sigurt.

Sending message with HMAC: [Ky është një mesazh i sigurt. | 3f2a1b9c4d...]
Server response: Message verified successfully. Integrity and authenticity confirmed.
```

Shkruaj `exit` për të dalë nga klienti.  
Shtyp `Ctrl+C` për të ndalur serverin.

---

## 📨 Formati i Protokollit

### Klienti → Serveri (JSON mbi TCP)

```json
{
  "message": "Ky është një mesazh i sigurt.",
  "hmac": "500db2e9d4c76f3842409d1d670d93bff88d380064f1a21a522bebf92321869a"
}
```

### Serveri → Klienti (tekst i thjeshtë)

| Situata | Përgjigja e serverit |
|---|---|
| HMAC i vlefshëm | `Message verified successfully. Integrity and authenticity confirmed.` |
| HMAC i pavlefshëm | `Error: Message verification failed! Integrity compromised.` |
| JSON i gabuar | `Error: Invalid message format. Expected JSON with 'message' and 'hmac' fields.` |
| Payload i paplotë | `Error: Payload missing 'message' or 'hmac' field.` |

---

## 🔒 Masat e Sigurisë

| Masa | Implementimi | Arsyeja |
|---|---|---|
| Timing-safe comparison | `hmac.compare_digest()` | Parandalon timing attacks ku sulmuesi mat kohën e krahasimit për të zbuluar HMAC-in byte pas byte |
| Funksioni hash | SHA-256 | Rezistent ndaj collision, 256-bit output, i besuar gjerësisht |
| Ruajtja e çelësit | Variabël mjedisi (`HMAC_SECRET`) | Çelësi nuk ruhet kurrë në kod burimor ose në git |
| Validimi i inputit | Kontrollo fushat bosh para verifikimit | Parandalon dërgimin e payload-eve të paplotë |

---

## 📁 Struktura e Projektit

```
projekt/
├── server.py      # Serveri: merr dhe verifikon mesazhe të nënshkruara me HMAC
├── client.py      # Klienti: nënshkruan mesazhet dhe i dërgon te serveri
└── README.md      # Ky skedar
```

---

## 🧪 Shembull i plotë i ekzekutimit

**Terminal 1 (Server):**
```
Server started and awaiting messages...
2026-05-04 12:00:00 - SERVER - INFO - Server listening on 127.0.0.1:65432
2026-05-04 12:00:10 - SERVER - INFO - Connection established with 127.0.0.1:54321

Message received with HMAC: [Pershendetje! | a1b2c3d4...]
Validating HMAC...
Message verified successfully. Integrity and authenticity confirmed.
2026-05-04 12:00:10 - SERVER - INFO - HMAC verification PASSED for message from 127.0.0.1:54321
```

**Terminal 2 (Client):**
```
2026-05-04 12:00:10 - CLIENT - INFO - Connected to server 127.0.0.1:65432

Enter your message (or 'exit' to quit): Pershendetje!
Sending message with HMAC: [Pershendetje! | a1b2c3d4...]
Server response: Message verified successfully. Integrity and authenticity confirmed.

Enter your message (or 'exit' to quit): exit
```

---
