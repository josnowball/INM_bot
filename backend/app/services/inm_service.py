"""
INM (Instituto Nacional de Migración) appointment booking service.

Target: https://citas.inm.gob.mx
Flow:
  1. Navigate to appointment page
  2. Select procedure type (trámite)
  3. Fill solicitud de estancia form with user profile data
  4. Select preferred office (delegación)
  5. Pick available date/time slot
  6. Confirm and capture confirmation code

This uses Playwright for browser automation. The government site
requires JavaScript rendering — no simple API available.
"""

from dataclasses import dataclass
from typing import Optional


# INM procedure types
INM_PROCEDURES = {
    "residencia_temporal": {
        "name": "Residencia Temporal",
        "description": "Temporary residence permit (1-4 years)",
        "category": "estancia",
    },
    "residencia_permanente": {
        "name": "Residencia Permanente",
        "description": "Permanent residence permit",
        "category": "estancia",
    },
    "cambio_condicion": {
        "name": "Cambio de Condición de Estancia",
        "description": "Change immigration status",
        "category": "estancia",
    },
    "renovacion_residencia": {
        "name": "Renovación de Residencia",
        "description": "Renew existing residence permit",
        "category": "estancia",
    },
    "permiso_salida_regreso": {
        "name": "Permiso de Salida y Regreso",
        "description": "Exit and re-entry permit",
        "category": "permiso",
    },
    "regularizacion": {
        "name": "Regularización Migratoria",
        "description": "Regularize immigration status",
        "category": "estancia",
    },
    "constancia_inscripcion_empleador": {
        "name": "Constancia de Inscripción de Empleador",
        "description": "Employer registration certificate",
        "category": "empleador",
    },
}

# Major INM offices
INM_OFFICES = {
    "cdmx_polanco": "Ciudad de México — Polanco",
    "cdmx_centro": "Ciudad de México — Centro",
    "guadalajara": "Guadalajara, Jalisco",
    "monterrey": "Monterrey, Nuevo León",
    "cancun": "Cancún, Quintana Roo",
    "merida": "Mérida, Yucatán",
    "puebla": "Puebla, Puebla",
    "tijuana": "Tijuana, Baja California",
    "leon": "León, Guanajuato",
    "queretaro": "Querétaro, Querétaro",
    "playa_del_carmen": "Playa del Carmen, Quintana Roo",
    "san_miguel_allende": "San Miguel de Allende, Guanajuato",
    "oaxaca": "Oaxaca, Oaxaca",
    "puerto_vallarta": "Puerto Vallarta, Jalisco",
}


@dataclass
class BookingResult:
    success: bool
    confirmation_code: Optional[str] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    office: Optional[str] = None
    error: Optional[str] = None


async def book_inm_appointment(
    procedure_type: str,
    user_profile: dict,
    preferred_office: Optional[str] = None,
    preferred_dates: Optional[list[str]] = None,
) -> BookingResult:
    """
    Automate INM appointment booking using Playwright.

    Args:
        procedure_type: Key from INM_PROCEDURES
        user_profile: Decrypted user profile dict
        preferred_office: Key from INM_OFFICES
        preferred_dates: List of ISO date strings in order of preference

    Returns:
        BookingResult with appointment details or error
    """
    if procedure_type not in INM_PROCEDURES:
        return BookingResult(success=False, error=f"Unknown procedure: {procedure_type}")

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
                # Step 1: Navigate to INM appointments
                await page.goto("https://citas.inm.gob.mx/", timeout=30000)
                await page.wait_for_load_state("networkidle")

                # Step 2: Select procedure type
                procedure = INM_PROCEDURES[procedure_type]
                # The exact selectors depend on the current INM site structure.
                # These are approximate and need to be updated based on the live site.

                # Look for the tramite/procedure selection
                tramite_selector = f'text="{procedure["name"]}"'
                tramite_el = page.locator(tramite_selector).first
                if await tramite_el.count() > 0:
                    await tramite_el.click()
                else:
                    # Try dropdown-based selection
                    select = page.locator('select[name*="tramite"], select[name*="procedure"]').first
                    if await select.count() > 0:
                        await select.select_option(label=procedure["name"])

                # Step 3: Fill the solicitud form with user data
                field_mapping = {
                    "nombre": user_profile.get("first_name", ""),
                    "apellido_paterno": user_profile.get("last_name", ""),
                    "apellido_materno": user_profile.get("middle_name", ""),
                    "nacionalidad": user_profile.get("nationality", ""),
                    "fecha_nacimiento": user_profile.get("birth_date", ""),
                    "pais_nacimiento": user_profile.get("birth_country", ""),
                    "sexo": user_profile.get("gender", ""),
                    "estado_civil": user_profile.get("marital_status", ""),
                    "pasaporte": user_profile.get("passport_number", ""),
                    "curp": user_profile.get("curp", ""),
                    "telefono": user_profile.get("phone", ""),
                    "calle": user_profile.get("address_street", ""),
                    "ciudad": user_profile.get("address_city", ""),
                    "estado": user_profile.get("address_state", ""),
                    "codigo_postal": user_profile.get("address_zip", ""),
                    "correo": user_profile.get("email", ""),
                }

                for field_key, value in field_mapping.items():
                    if not value:
                        continue
                    # Try multiple selector patterns
                    for selector in [
                        f'input[name*="{field_key}"]',
                        f'input[id*="{field_key}"]',
                        f'input[placeholder*="{field_key}"]',
                    ]:
                        el = page.locator(selector).first
                        if await el.count() > 0:
                            await el.fill(value)
                            break

                # Step 4: Select office
                if preferred_office and preferred_office in INM_OFFICES:
                    office_name = INM_OFFICES[preferred_office]
                    office_select = page.locator('select[name*="delegacion"], select[name*="oficina"]').first
                    if await office_select.count() > 0:
                        await office_select.select_option(label=office_name)

                # Step 5: Find and select available date/time
                # This depends heavily on the INM site's date picker implementation
                submit_btn = page.locator('button[type="submit"], input[type="submit"]').first
                if await submit_btn.count() > 0:
                    await submit_btn.click()
                    await page.wait_for_load_state("networkidle")

                # Step 6: Try to capture confirmation
                # Look for confirmation elements
                confirmation_el = page.locator('[class*="confirm"], [id*="confirm"], [class*="folio"]').first
                confirmation_code = None
                if await confirmation_el.count() > 0:
                    confirmation_code = await confirmation_el.text_content()

                # Get appointment details from the page
                appointment_date = None
                appointment_time = None
                date_el = page.locator('[class*="fecha"], [class*="date"]').first
                if await date_el.count() > 0:
                    appointment_date = await date_el.text_content()

                time_el = page.locator('[class*="hora"], [class*="time"]').first
                if await time_el.count() > 0:
                    appointment_time = await time_el.text_content()

                office_text = INM_OFFICES.get(preferred_office, "Not specified")

                return BookingResult(
                    success=True,
                    confirmation_code=confirmation_code,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    office=office_text,
                )

            except Exception as e:
                # Take screenshot for debugging
                await page.screenshot(path="/tmp/inm_error.png")
                return BookingResult(success=False, error=str(e))

            finally:
                await browser.close()

    except ImportError:
        return BookingResult(
            success=False,
            error="Playwright not installed. Run: pip install playwright && playwright install chromium",
        )
    except Exception as e:
        return BookingResult(success=False, error=str(e))


def get_solicitud_fields(procedure_type: str) -> dict:
    """
    Return the required fields for a solicitud de estancia form,
    organized by section, so the frontend can show a guided form.
    """
    base_fields = {
        "personal": {
            "title": "Datos Personales",
            "fields": [
                {"key": "first_name", "label": "Nombre(s)", "required": True},
                {"key": "last_name", "label": "Apellido Paterno", "required": True},
                {"key": "middle_name", "label": "Apellido Materno", "required": False},
                {"key": "birth_date", "label": "Fecha de Nacimiento", "type": "date", "required": True},
                {"key": "birth_country", "label": "País de Nacimiento", "required": True},
                {"key": "birth_state", "label": "Estado de Nacimiento", "required": False},
                {"key": "nationality", "label": "Nacionalidad", "required": True},
                {"key": "gender", "label": "Sexo", "type": "select", "options": ["Masculino", "Femenino"], "required": True},
                {"key": "marital_status", "label": "Estado Civil", "type": "select",
                 "options": ["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Unión Libre"], "required": True},
            ],
        },
        "documents": {
            "title": "Documentos",
            "fields": [
                {"key": "passport_number", "label": "Número de Pasaporte", "required": True},
                {"key": "passport_country", "label": "País Emisor del Pasaporte", "required": True},
                {"key": "passport_expiry", "label": "Vigencia del Pasaporte", "type": "date", "required": True},
                {"key": "curp", "label": "CURP (si aplica)", "required": False},
            ],
        },
        "contact": {
            "title": "Datos de Contacto",
            "fields": [
                {"key": "phone", "label": "Teléfono", "required": True},
                {"key": "address_street", "label": "Calle y Número", "required": True},
                {"key": "address_city", "label": "Ciudad / Municipio", "required": True},
                {"key": "address_state", "label": "Estado", "required": True},
                {"key": "address_zip", "label": "Código Postal", "required": True},
                {"key": "address_country", "label": "País", "required": True},
            ],
        },
    }

    # Add procedure-specific fields
    proc = INM_PROCEDURES.get(procedure_type, {})
    if proc.get("category") == "estancia":
        base_fields["immigration"] = {
            "title": "Datos Migratorios",
            "fields": [
                {"key": "immigration_status", "label": "Condición de Estancia Actual", "required": True},
                {"key": "entry_date", "label": "Fecha de Entrada a México", "type": "date", "required": True},
                {"key": "permit_number", "label": "Número de Permiso / Tarjeta", "required": False},
            ],
        }

    return base_fields
