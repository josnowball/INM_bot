# Security Policy — CitaFacil

## How we protect your data

### Encryption at rest (AES-256-GCM)
Every personal data field (name, passport number, CURP, address, etc.) is encrypted
with AES-256-GCM before being written to the database. Each field gets a unique random
nonce, so even identical values produce different ciphertext. The encryption key is
stored as an environment variable — never in the database or code.

If the database were compromised, the attacker would see only encrypted blobs, not
your personal information.

### MiConsulado credentials
For SRE bookings, you provide your MiConsulado email and password. These are:
- Used **once** during the booking session
- Passed directly to the browser automation engine
- **Never written to the database** or any log file
- Cleared from memory as soon as the booking completes or fails
- On Telegram, we attempt to delete the password message automatically

We **do not** create MiConsulado accounts on your behalf. You must already have one.

### Password hashing
Your CitaFacil account password is hashed with bcrypt (work factor 12) before storage.
We cannot reverse your password. If you forget it, you must reset it.

### Authentication
- JWT access tokens with 1-hour expiry
- Refresh tokens with 7-day expiry
- Tokens are invalidated on logout

### Transport security
- All production traffic must use HTTPS (TLS 1.2+)
- CORS is restricted to known frontend origins
- Rate limiting on authentication endpoints

### Minimal data collection
We only collect data that is strictly required to fill out government appointment forms.
We do not:
- Track user behavior
- Use analytics cookies
- Sell or share data with third parties
- Store data longer than needed

### Infrastructure
- Database: Encrypted SQLite (dev) / PostgreSQL with encrypted connections (prod)
- Secrets: Environment variables only — never in code or version control
- Docker: Non-root containers, minimal base images

## Reporting vulnerabilities
If you discover a security issue, please email security@citafacil.app.
Do not open a public GitHub issue for security vulnerabilities.

## Data deletion
Users can request complete account and data deletion at any time.
All encrypted personal data is permanently removed from the database.
