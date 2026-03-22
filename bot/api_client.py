"""
CitaFacil API client — async httpx wrapper for bot → backend communication.
"""

import asyncio
import httpx
import os
from typing import Optional


class CitaFacilAPI:
    """Async HTTP client for all backend API calls."""

    def __init__(self, base_url: str = None, timeout: float = 30.0):
        self.base_url = (base_url or os.getenv("API_BASE_URL", "http://localhost:8000")).rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._client

    def _auth_headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ── Auth ──────────────────────────────────────────────────────────

    async def register(self, email: str, password: str, full_name: str = None,
                       telegram_chat_id: str = None) -> dict:
        """Register a new user. Returns tokens."""
        client = await self._get_client()
        payload = {"email": email, "password": password}
        if full_name:
            payload["full_name"] = full_name
        if telegram_chat_id:
            payload["telegram_chat_id"] = telegram_chat_id

        resp = await client.post("/api/auth/telegram-register", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def login_by_telegram(self, telegram_chat_id: str) -> Optional[dict]:
        """Login by Telegram chat ID. Returns tokens or None if not linked."""
        client = await self._get_client()
        resp = await client.post(
            "/api/auth/telegram-login",
            json={"telegram_chat_id": telegram_chat_id},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def login(self, email: str, password: str) -> dict:
        """Login with email/password. Returns tokens."""
        client = await self._get_client()
        resp = await client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        resp.raise_for_status()
        return resp.json()

    async def verify_email(self, token: str, code: str) -> dict:
        client = await self._get_client()
        resp = await client.post(
            "/api/auth/verify-email",
            json={"code": code},
            headers=self._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json()

    async def get_me(self, token: str) -> dict:
        client = await self._get_client()
        resp = await client.get("/api/auth/me", headers=self._auth_headers(token))
        resp.raise_for_status()
        return resp.json()

    # ── Profile ───────────────────────────────────────────────────────

    async def get_profile(self, token: str) -> dict:
        client = await self._get_client()
        resp = await client.get("/api/profile/", headers=self._auth_headers(token))
        resp.raise_for_status()
        return resp.json()

    async def update_profile(self, token: str, data: dict) -> dict:
        client = await self._get_client()
        resp = await client.put(
            "/api/profile/",
            json=data,
            headers=self._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json()

    # ── Appointments ──────────────────────────────────────────────────

    async def book_inm(self, token: str, procedure_type: str,
                       preferred_office: str = None,
                       preferred_dates: list = None) -> dict:
        client = await self._get_client()
        payload = {"procedure_type": procedure_type}
        if preferred_office:
            payload["preferred_office"] = preferred_office
        if preferred_dates:
            payload["preferred_dates"] = preferred_dates

        resp = await client.post(
            "/api/appointments/inm/book",
            json=payload,
            headers=self._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json()

    async def book_sre(self, token: str, procedure_type: str,
                       mi_consulado_email: str, mi_consulado_password: str,
                       preferred_office: str = None,
                       preferred_dates: list = None) -> dict:
        client = await self._get_client()
        payload = {
            "procedure_type": procedure_type,
            "mi_consulado_email": mi_consulado_email,
            "mi_consulado_password": mi_consulado_password,
        }
        if preferred_office:
            payload["preferred_office"] = preferred_office
        if preferred_dates:
            payload["preferred_dates"] = preferred_dates

        resp = await client.post(
            "/api/appointments/sre/book",
            json=payload,
            headers=self._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json()

    async def check_sre_slots(self, token: str, procedure_type: str,
                              mi_consulado_email: str, mi_consulado_password: str,
                              preferred_office: str = None) -> dict:
        """Check available SRE appointment slots without booking."""
        client = await self._get_client()
        payload = {
            "procedure_type": procedure_type,
            "mi_consulado_email": mi_consulado_email,
            "mi_consulado_password": mi_consulado_password,
        }
        if preferred_office:
            payload["preferred_office"] = preferred_office

        resp = await client.post(
            "/api/appointments/sre/check-slots",
            json=payload,
            headers=self._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json()

    async def confirm_sre_slot(self, token: str, session_id: str,
                               date: str, time: str) -> dict:
        """Confirm a specific slot from check_sre_slots."""
        client = await self._get_client()
        resp = await client.post(
            "/api/appointments/sre/confirm-slot",
            json={"session_id": session_id, "date": date, "time": time},
            headers=self._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json()

    async def get_appointment(self, token: str, appointment_id: str) -> dict:
        client = await self._get_client()
        resp = await client.get(
            f"/api/appointments/{appointment_id}",
            headers=self._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json()

    async def list_appointments(self, token: str) -> list:
        client = await self._get_client()
        resp = await client.get(
            "/api/appointments/",
            headers=self._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json()

    async def poll_appointment_status(self, token: str, appointment_id: str,
                                       max_wait: int = 300, interval: int = 10) -> dict:
        """Poll until appointment status is terminal (booked/failed) or timeout."""
        elapsed = 0
        while elapsed < max_wait:
            appt = await self.get_appointment(token, appointment_id)
            if appt["status"] in ("booked", "failed"):
                return appt
            await asyncio.sleep(interval)
            elapsed += interval

        # Timeout — return last known status
        return await self.get_appointment(token, appointment_id)

    # ── CAPTCHA relay ─────────────────────────────────────────────────

    async def get_pending_captcha(self, token: str) -> Optional[dict]:
        """Check if there's a CAPTCHA waiting to be solved."""
        client = await self._get_client()
        resp = await client.get(
            "/api/captcha/pending",
            headers=self._auth_headers(token),
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def submit_captcha_solution(self, token: str, captcha_id: str,
                                       solution: str) -> dict:
        """Submit user's CAPTCHA solution."""
        client = await self._get_client()
        resp = await client.post(
            "/api/captcha/solve",
            json={"captcha_id": captcha_id, "solution": solution},
            headers=self._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json()
