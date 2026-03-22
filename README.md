# CitaFacil — One-Click Appointment Booking for INM & SRE

Skip the headache of navigating Mexican government websites. Fill in your profile once, and we handle the dozens of clicks, form fields, and page loads for you.

## What it does

- **INM (Immigration):** Books appointments for residencia temporal/permanente, cambio de condicion, regularizacion, and more. Auto-fills the solicitud de estancia correctly.
- **SRE (Passports & Visas):** Books appointments via MiConsulado for passports, visa exchanges, apostille, and more. You provide your own MiConsulado login (we never store it).
- **Telegram Bot:** Book appointments directly from Telegram with a guided conversation flow.
- **Web App:** Full dashboard with profile management, appointment tracking, and booking.

## Architecture

```
frontend/          React + Vite (SPA)
backend/           FastAPI + SQLAlchemy + Playwright
bot/               python-telegram-bot
docker-compose.yml Full stack deployment
```

## Security

All personal data is encrypted at rest with AES-256-GCM. MiConsulado credentials are used once and never stored. See [SECURITY.md](SECURITY.md) for full details.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Telegram bot token (from @BotFather)

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Generate keys
python -c "import os; print('SECRET_KEY=' + os.urandom(32).hex()); print('ENCRYPTION_KEY=' + os.urandom(32).hex())"

# Copy and edit .env
cp .env.example .env
# Edit .env with your keys and settings

uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Telegram Bot
```bash
export TELEGRAM_BOT_TOKEN=your-token-here
cd bot
python bot.py
```

### Docker (all at once)
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with real values
docker-compose up --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/verify-email` | Verify email with code |
| GET | `/api/auth/me` | Current user |
| GET | `/api/profile/` | Get profile (decrypted) |
| PUT | `/api/profile/` | Update profile (encrypted) |
| GET | `/api/appointments/inm/procedures` | List INM procedures |
| GET | `/api/appointments/inm/offices` | List INM offices |
| POST | `/api/appointments/inm/book` | Book INM appointment |
| GET | `/api/appointments/sre/procedures` | List SRE procedures |
| POST | `/api/appointments/sre/book` | Book SRE appointment |
| GET | `/api/appointments/` | List user's appointments |
| GET | `/api/health` | Health check |

## How the automation works

1. User fills in their profile once (name, passport, CURP, address, etc.)
2. User selects a procedure and office
3. Backend spins up a headless Chromium browser via Playwright
4. Navigates to the government site (citas.inm.gob.mx or citas.sre.gob.mx)
5. Auto-fills all form fields with the user's encrypted profile data
6. Selects the preferred office and available time slot
7. Returns confirmation code to the user

**Note:** Government sites may change their structure at any time. The Playwright selectors in `services/inm_service.py` and `services/sre_service.py` may need updating. This is the nature of web automation against third-party sites.

## Disclaimer

CitaFacil is not affiliated with INM, SRE, or any Mexican government agency. We are an independent tool that automates the public appointment booking process. Use at your own discretion.
