"""
SRE (Secretaría de Relaciones Exteriores) / MiConsulado appointment booking.

Target: https://citas.sre.gob.mx / MiConsulado portal
Flow:
  1. User provides their own MiConsulado email + password (we do NOT store these)
  2. We log in on their behalf
  3. Fill the appointment form with profile data
  4. Select preferred office and date
  5. Confirm and capture confirmation

IMPORTANT: We never store MiConsulado credentials. They are used once
during the booking session and immediately discarded.
"""

from dataclasses import dataclass
from typing import Optional


SRE_PROCEDURES = {
    "pasaporte_primera_vez": {
        "name": "Pasaporte — Primera Vez",
        "description": "First-time passport application",
    },
    "pasaporte_renovacion": {
        "name": "Pasaporte — Renovación",
        "description": "Passport renewal",
    },
    "visa_canje": {
        "name": "Canje de Visa",
        "description": "Exchange/replace visa",
    },
    "carta_naturalizacion": {
        "name": "Carta de Naturalización",
        "description": "Naturalization letter",
    },
    "apostilla": {
        "name": "Apostilla",
        "description": "Document apostille",
    },
    "legalizacion": {
        "name": "Legalización de Documentos",
        "description": "Document legalization",
    },
    "registro_civil": {
        "name": "Registro Civil",
        "description": "Civil registry services",
    },
}

SRE_OFFICES = {
    "cdmx_tlatelolco": "Ciudad de México — Tlatelolco",
    "cdmx_polanco": "Ciudad de México — Polanco",
    "guadalajara": "Guadalajara, Jalisco",
    "monterrey": "Monterrey, Nuevo León",
    "puebla": "Puebla, Puebla",
    "cancun": "Cancún, Quintana Roo",
    "merida": "Mérida, Yucatán",
    "tijuana": "Tijuana, Baja California",
    "queretaro": "Querétaro, Querétaro",
    "leon": "León, Guanajuato",
}


@dataclass
class SREBookingResult:
    success: bool
    confirmation_code: Optional[str] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    office: Optional[str] = None
    error: Optional[str] = None


async def book_sre_appointment(
    procedure_type: str,
    mi_consulado_email: str,
    mi_consulado_password: str,
    user_profile: dict,
    preferred_office: Optional[str] = None,
    preferred_dates: Optional[list[str]] = None,
) -> SREBookingResult:
    """
    Automate SRE/MiConsulado appointment booking.

    IMPORTANT: mi_consulado_email and mi_consulado_password are used ONLY
    for this session and are NOT stored anywhere.
    """
    if procedure_type not in SRE_PROCEDURES:
        return SREBookingResult(success=False, error=f"Unknown procedure: {procedure_type}")

    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                locale="es-MX",
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            )
            page = await context.new_page()

            try:
                # Step 1: Navigate to MiConsulado / SRE appointments
                await page.goto("https://citas.sre.gob.mx/", timeout=30000)
                await page.wait_for_load_state("networkidle")

                # Step 2: Login with user's MiConsulado credentials
                email_input = page.locator('input[type="email"], input[name*="email"], input[name*="correo"]').first
                if await email_input.count() > 0:
                    await email_input.fill(mi_consulado_email)

                pass_input = page.locator('input[type="password"]').first
                if await pass_input.count() > 0:
                    await pass_input.fill(mi_consulado_password)

                login_btn = page.locator('button[type="submit"], input[type="submit"]').first
                if await login_btn.count() > 0:
                    await login_btn.click()
                    await page.wait_for_load_state("networkidle")

                # Step 3: Select procedure
                procedure = SRE_PROCEDURES[procedure_type]
                proc_link = page.locator(f'text="{procedure["name"]}"').first
                if await proc_link.count() > 0:
                    await proc_link.click()
                    await page.wait_for_load_state("networkidle")

                # Step 4: Fill form fields from profile
                field_mapping = {
                    "nombre": user_profile.get("first_name", ""),
                    "paterno": user_profile.get("last_name", ""),
                    "materno": user_profile.get("middle_name", ""),
                    "nacimiento": user_profile.get("birth_date", ""),
                    "nacionalidad": user_profile.get("nationality", ""),
                    "curp": user_profile.get("curp", ""),
                    "telefono": user_profile.get("phone", ""),
                    "correo": user_profile.get("email", ""),
                }

                for field_key, value in field_mapping.items():
                    if not value:
                        continue
                    for selector in [
                        f'input[name*="{field_key}"]',
                        f'input[id*="{field_key}"]',
                    ]:
                        el = page.locator(selector).first
                        if await el.count() > 0:
                            await el.fill(value)
                            break

                # Step 5: Select office
                if preferred_office and preferred_office in SRE_OFFICES:
                    office_name = SRE_OFFICES[preferred_office]
                    office_select = page.locator('select[name*="delegacion"], select[name*="oficina"]').first
                    if await office_select.count() > 0:
                        await office_select.select_option(label=office_name)

                # Step 6: Submit and capture confirmation
                submit = page.locator('button[type="submit"], input[type="submit"]').first
                if await submit.count() > 0:
                    await submit.click()
                    await page.wait_for_load_state("networkidle")

                confirmation_el = page.locator('[class*="confirm"], [id*="confirm"], [class*="folio"]').first
                confirmation_code = None
                if await confirmation_el.count() > 0:
                    confirmation_code = await confirmation_el.text_content()

                office_text = SRE_OFFICES.get(preferred_office, "Not specified")

                return SREBookingResult(
                    success=True,
                    confirmation_code=confirmation_code,
                    office=office_text,
                )

            except Exception as e:
                await page.screenshot(path="/tmp/sre_error.png")
                return SREBookingResult(success=False, error=str(e))

            finally:
                # Ensure credentials are not retained in browser state
                await context.clear_cookies()
                await browser.close()

    except ImportError:
        return SREBookingResult(
            success=False,
            error="Playwright not installed. Run: pip install playwright && playwright install chromium",
        )
    except Exception as e:
        return SREBookingResult(success=False, error=str(e))


# ── Interactive slot flow ─────────────────────────────────────────────

# In-memory browser sessions for slot selection
_active_sessions: dict[str, dict] = {}


async def check_available_slots(
    procedure_type: str,
    mi_consulado_email: str,
    mi_consulado_password: str,
    user_profile: dict,
    preferred_office: str = None,
    session_id: str = "",
    telegram_chat_id: str = "",
) -> dict:
    """
    Navigate the SRE site through to the calendar page and return available slots.
    Keeps the browser session alive for confirm_slot() to resume.
    """
    try:
        from playwright.async_api import async_playwright
        from app.services.captcha_service import solve_captcha
        from app.services.slot_picker import parse_sre_calendar, get_time_slots_for_date

        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="es-MX",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
        )
        page = await context.new_page()

        try:
            # Navigate to SRE site
            await page.goto("https://citas.sre.gob.mx/", wait_until="networkidle", timeout=30000)

            # Handle CAPTCHA if present
            if telegram_chat_id:
                await solve_captcha(page, telegram_chat_id)

            # Login
            email_input = page.locator('input[type="email"], input[name*="email"], input[name*="correo"]').first
            if await email_input.count() > 0:
                await email_input.fill(mi_consulado_email)
                await page.wait_for_timeout(300)

            pass_input = page.locator('input[type="password"]').first
            if await pass_input.count() > 0:
                await pass_input.fill(mi_consulado_password)
                await page.wait_for_timeout(300)

            submit_btn = page.locator('button[type="submit"], input[type="submit"], button:has-text("Iniciar"), button:has-text("Login")').first
            if await submit_btn.count() > 0:
                await submit_btn.click()
                await page.wait_for_load_state("networkidle", timeout=15000)

            # Handle post-login CAPTCHA
            if telegram_chat_id:
                await solve_captcha(page, telegram_chat_id)

            # Select procedure (click through form steps)
            proc_name = SRE_PROCEDURES.get(procedure_type, procedure_type)
            proc_el = page.locator(f'text="{proc_name}"').first
            if await proc_el.count() > 0:
                await proc_el.click()
                await page.wait_for_timeout(2000)

            # Fill profile data into form fields
            field_map = {
                "nombre": user_profile.get("first_name", ""),
                "paterno": user_profile.get("last_name", ""),
                "nacimiento": user_profile.get("birth_date", ""),
                "nacionalidad": user_profile.get("nationality", ""),
                "curp": user_profile.get("curp", ""),
                "telefono": user_profile.get("phone", ""),
                "correo": user_profile.get("email", ""),
                "pasaporte": user_profile.get("passport_number", ""),
            }

            for field_key, value in field_map.items():
                if not value:
                    continue
                for sel in [f'[name*="{field_key}"]', f'[id*="{field_key}"]']:
                    try:
                        el = page.locator(sel).first
                        if await el.count() > 0:
                            await el.fill(value)
                            await page.wait_for_timeout(200)
                            break
                    except Exception:
                        continue

            # Select office
            if preferred_office:
                office_name = SRE_OFFICES.get(preferred_office, preferred_office)
                try:
                    await page.select_option('select', label=office_name)
                except Exception:
                    try:
                        office_el = page.locator(f'text="{office_name}"').first
                        if await office_el.count() > 0:
                            await office_el.click()
                    except Exception:
                        pass

            # Navigate to calendar (click next/continue buttons)
            for btn_text in ["Siguiente", "Continuar", "Next", "Continue"]:
                try:
                    btn = page.locator(f'button:has-text("{btn_text}"), a:has-text("{btn_text}")').first
                    if await btn.count() > 0:
                        await btn.click()
                        await page.wait_for_timeout(3000)
                except Exception:
                    continue

            # Parse available dates from calendar
            date_slots = await parse_sre_calendar(page)

            # For each available date, also check time slots
            all_slots = []
            for ds in date_slots[:5]:  # Check top 5 dates
                time_slots = await get_time_slots_for_date(page, None)  # TODO: pass element
                if time_slots:
                    for ts in time_slots:
                        all_slots.append({
                            "date": ds.date,
                            "time": ts.time,
                            "availability": ds.availability,
                        })
                else:
                    all_slots.append({
                        "date": ds.date,
                        "time": "09:00",  # Default if no specific times
                        "availability": ds.availability,
                    })

            # Store session for later confirmation
            _active_sessions[session_id] = {
                "pw": pw,
                "browser": browser,
                "context": context,
                "page": page,
            }

            return {"slots": all_slots, "session_id": session_id}

        except Exception as e:
            await page.screenshot(path="/tmp/sre_slots_error.png")
            await browser.close()
            await pw.stop()
            raise e

    except ImportError:
        raise RuntimeError("Playwright not installed")


async def confirm_slot(session_id: str, date: str, time: str) -> dict:
    """Resume an active browser session and click the selected slot."""
    session = _active_sessions.pop(session_id, None)
    if not session:
        return {"success": False, "error": "Session expired"}

    page = session["page"]
    browser = session["browser"]
    pw = session["pw"]

    try:
        from app.services.slot_picker import select_slot as pick_slot

        # Click the selected date and time
        clicked = await pick_slot(page, date, time)
        if not clicked:
            return {"success": False, "error": "Could not select the chosen slot"}

        # Click confirm/submit
        for btn_text in ["Confirmar", "Agendar", "Confirm", "Submit"]:
            try:
                btn = page.locator(f'button:has-text("{btn_text}")').first
                if await btn.count() > 0:
                    await btn.click()
                    await page.wait_for_timeout(5000)
                    break
            except Exception:
                continue

        # Extract confirmation code
        confirmation_code = None
        for sel in ['[class*="confirm"]', '[class*="folio"]', '[id*="confirm"]']:
            try:
                el = page.locator(sel).first
                if await el.count() > 0:
                    confirmation_code = await el.text_content()
                    break
            except Exception:
                continue

        return {
            "success": True,
            "confirmation_code": confirmation_code,
            "date": date,
            "time": time,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

    finally:
        try:
            context = session.get("context")
            if context:
                await context.clear_cookies()
            await browser.close()
            await pw.stop()
        except Exception:
            pass
