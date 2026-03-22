from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# --- Auth ---

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class VerifyEmailRequest(BaseModel):
    code: str


# --- Profile ---

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    nationality: Optional[str] = None
    birth_date: Optional[str] = None
    birth_country: Optional[str] = None
    birth_state: Optional[str] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    passport_number: Optional[str] = None
    passport_country: Optional[str] = None
    passport_expiry: Optional[str] = None
    curp: Optional[str] = None
    phone: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None
    address_country: Optional[str] = None
    immigration_status: Optional[str] = None
    entry_date: Optional[str] = None
    permit_number: Optional[str] = None


class ProfileResponse(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    nationality: Optional[str] = None
    birth_date: Optional[str] = None
    birth_country: Optional[str] = None
    birth_state: Optional[str] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    passport_number: Optional[str] = None
    passport_country: Optional[str] = None
    passport_expiry: Optional[str] = None
    curp: Optional[str] = None
    phone: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None
    address_country: Optional[str] = None
    immigration_status: Optional[str] = None
    entry_date: Optional[str] = None
    permit_number: Optional[str] = None
    completion_pct: int = 0


# --- Appointments ---

class INMBookingRequest(BaseModel):
    procedure_type: str  # e.g. "residencia_temporal", "residencia_permanente", "cambio_condicion"
    preferred_office: Optional[str] = None  # INM office code
    preferred_dates: Optional[list[str]] = None  # ISO dates


class SREBookingRequest(BaseModel):
    procedure_type: str  # e.g. "visa_canje", "permiso_salida"
    mi_consulado_email: str  # user's MiConsulado email
    mi_consulado_password: str  # user's MiConsulado password (NOT stored — used once)
    preferred_office: Optional[str] = None
    preferred_dates: Optional[list[str]] = None


class AppointmentResponse(BaseModel):
    id: str
    service: str
    procedure_type: str
    status: str
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    office_location: Optional[str] = None
    confirmation_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    id: str
    email: str
    email_verified: bool
    full_name: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Telegram Auth ---

class TelegramRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    telegram_chat_id: str


class TelegramLoginRequest(BaseModel):
    telegram_chat_id: str


# --- Slot Selection ---

class AvailableSlot(BaseModel):
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    availability: str  # "high", "medium", "low"


class SlotCheckResponse(BaseModel):
    session_id: str
    slots: list[AvailableSlot]
    expires_in_seconds: int = 300


class SlotConfirmRequest(BaseModel):
    session_id: str
    date: str
    time: str


# --- CAPTCHA ---

class CaptchaPendingResponse(BaseModel):
    captcha_id: str
    image_url: str  # base64 data URL or path
    captcha_type: str  # "image", "recaptcha_v2", etc.


class CaptchaSolveRequest(BaseModel):
    captcha_id: str
    solution: str
