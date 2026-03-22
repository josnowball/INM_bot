from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserProfile, Appointment
from app.schemas import (
    INMBookingRequest, SREBookingRequest, AppointmentResponse,
    SlotCheckResponse, SlotConfirmRequest, AvailableSlot,
    CaptchaPendingResponse, CaptchaSolveRequest,
)
from app.auth import get_current_user
from app.encryption import decrypt
from app.services.inm_service import book_inm_appointment, INM_PROCEDURES, INM_OFFICES, get_solicitud_fields
from app.services.sre_service import book_sre_appointment, SRE_PROCEDURES, SRE_OFFICES

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


def _decrypt_profile_dict(profile: UserProfile) -> dict:
    """Get all decrypted profile fields as a dict."""
    data = {}
    for col in UserProfile.__table__.columns:
        if col.name.startswith("enc_"):
            raw = getattr(profile, col.name)
            data[col.name[4:]] = decrypt(raw) if raw else None
    return data


# --- Reference data ---

@router.get("/inm/procedures")
async def list_inm_procedures():
    return INM_PROCEDURES


@router.get("/inm/offices")
async def list_inm_offices():
    return INM_OFFICES


@router.get("/inm/solicitud-fields/{procedure_type}")
async def get_inm_solicitud_fields(procedure_type: str):
    if procedure_type not in INM_PROCEDURES:
        raise HTTPException(status_code=404, detail="Unknown procedure")
    return get_solicitud_fields(procedure_type)


@router.get("/sre/procedures")
async def list_sre_procedures():
    return SRE_PROCEDURES


@router.get("/sre/offices")
async def list_sre_offices():
    return SRE_OFFICES


# --- Booking ---

async def _run_inm_booking(appointment_id: str, procedure_type: str, profile_data: dict, office: str, dates: list):
    """Background task to run the INM booking automation."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appt:
            return

        appt.status = "in_progress"
        db.commit()

        result = await book_inm_appointment(
            procedure_type=procedure_type,
            user_profile=profile_data,
            preferred_office=office,
            preferred_dates=dates,
        )

        if result.success:
            appt.status = "booked"
            appt.confirmation_code = result.confirmation_code
            appt.appointment_date = result.appointment_date
            appt.appointment_time = result.appointment_time
            appt.office_location = result.office
        else:
            appt.status = "failed"
            appt.error_message = result.error

        db.commit()
    finally:
        db.close()


@router.post("/inm/book", response_model=AppointmentResponse)
async def book_inm(
    req: INMBookingRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.email_verified:
        raise HTTPException(status_code=400, detail="Please verify your email first")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile or not profile.enc_first_name:
        raise HTTPException(status_code=400, detail="Please complete your profile first")

    profile_data = _decrypt_profile_dict(profile)
    profile_data["email"] = user.email

    appt = Appointment(
        user_id=user.id,
        service="inm",
        procedure_type=req.procedure_type,
        status="pending",
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)

    background_tasks.add_task(
        _run_inm_booking,
        appt.id,
        req.procedure_type,
        profile_data,
        req.preferred_office,
        req.preferred_dates,
    )

    return AppointmentResponse(
        id=appt.id,
        service=appt.service,
        procedure_type=appt.procedure_type,
        status=appt.status,
        created_at=appt.created_at,
        updated_at=appt.updated_at,
    )


async def _run_sre_booking(appointment_id: str, procedure_type: str, email: str, password: str, profile_data: dict, office: str, dates: list):
    """Background task for SRE booking. Credentials used once and discarded."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appt:
            return

        appt.status = "in_progress"
        db.commit()

        result = await book_sre_appointment(
            procedure_type=procedure_type,
            mi_consulado_email=email,
            mi_consulado_password=password,
            user_profile=profile_data,
            preferred_office=office,
            preferred_dates=dates,
        )

        if result.success:
            appt.status = "booked"
            appt.confirmation_code = result.confirmation_code
            appt.appointment_date = result.appointment_date
            appt.appointment_time = result.appointment_time
            appt.office_location = result.office
        else:
            appt.status = "failed"
            appt.error_message = result.error

        db.commit()
    finally:
        db.close()


@router.post("/sre/book", response_model=AppointmentResponse)
async def book_sre(
    req: SREBookingRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.email_verified:
        raise HTTPException(status_code=400, detail="Please verify your email first")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Please complete your profile first")

    profile_data = _decrypt_profile_dict(profile)
    profile_data["email"] = user.email

    appt = Appointment(
        user_id=user.id,
        service="sre",
        procedure_type=req.procedure_type,
        status="pending",
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)

    # Pass credentials to background task — they are NOT stored in DB
    background_tasks.add_task(
        _run_sre_booking,
        appt.id,
        req.procedure_type,
        req.mi_consulado_email,
        req.mi_consulado_password,
        profile_data,
        req.preferred_office,
        req.preferred_dates,
    )

    return AppointmentResponse(
        id=appt.id,
        service=appt.service,
        procedure_type=appt.procedure_type,
        status=appt.status,
        created_at=appt.created_at,
        updated_at=appt.updated_at,
    )


# --- List / Status ---

@router.get("/", response_model=list[AppointmentResponse])
async def list_appointments(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appts = (
        db.query(Appointment)
        .filter(Appointment.user_id == user.id)
        .order_by(Appointment.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        AppointmentResponse(
            id=a.id, service=a.service, procedure_type=a.procedure_type,
            status=a.status, appointment_date=a.appointment_date,
            appointment_time=a.appointment_time, office_location=a.office_location,
            confirmation_code=a.confirmation_code, error_message=a.error_message,
            created_at=a.created_at, updated_at=a.updated_at,
        )
        for a in appts
    ]


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appt = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id, Appointment.user_id == user.id)
        .first()
    )
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return AppointmentResponse(
        id=appt.id, service=appt.service, procedure_type=appt.procedure_type,
        status=appt.status, appointment_date=appt.appointment_date,
        appointment_time=appt.appointment_time, office_location=appt.office_location,
        confirmation_code=appt.confirmation_code, error_message=appt.error_message,
        created_at=appt.created_at, updated_at=appt.updated_at,
    )


# --- Slot Check / Confirm (SRE interactive flow) ---

import uuid
import asyncio

# In-memory session store for browser contexts awaiting slot confirmation
_browser_sessions: dict[str, dict] = {}


@router.post("/sre/check-slots", response_model=SlotCheckResponse)
async def check_sre_slots(
    req: SREBookingRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Navigate to SRE site, fill forms, and return available calendar slots."""
    if not user.email_verified:
        raise HTTPException(status_code=400, detail="Please verify your email first")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Please complete your profile first")

    profile_data = _decrypt_profile_dict(profile)
    profile_data["email"] = user.email

    # Run Playwright to navigate to calendar page and extract slots
    from app.services.sre_service import check_available_slots

    session_id = str(uuid.uuid4())

    try:
        result = await check_available_slots(
            procedure_type=req.procedure_type,
            mi_consulado_email=req.mi_consulado_email,
            mi_consulado_password=req.mi_consulado_password,
            user_profile=profile_data,
            preferred_office=req.preferred_office,
            session_id=session_id,
            telegram_chat_id=user.telegram_chat_id,
        )

        slots = [
            AvailableSlot(date=s["date"], time=s["time"], availability=s.get("availability", "medium"))
            for s in result.get("slots", [])
        ]

        # Store session for later confirmation (browser stays open)
        _browser_sessions[session_id] = {
            "user_id": user.id,
            "created_at": asyncio.get_event_loop().time(),
        }

        # Auto-cleanup after 5 minutes
        asyncio.get_event_loop().call_later(300, lambda: _browser_sessions.pop(session_id, None))

        return SlotCheckResponse(
            session_id=session_id,
            slots=slots,
            expires_in_seconds=300,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Slot check failed: {str(e)}")


@router.post("/sre/confirm-slot", response_model=AppointmentResponse)
async def confirm_sre_slot(
    req: SlotConfirmRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Confirm a specific slot from a check-slots session."""
    session = _browser_sessions.pop(req.session_id, None)
    if not session:
        raise HTTPException(status_code=404, detail="Session expired or not found")

    if session["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Session belongs to another user")

    from app.services.sre_service import confirm_slot

    appt = Appointment(
        user_id=user.id,
        service="sre",
        procedure_type="slot_confirm",
        status="in_progress",
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)

    try:
        result = await confirm_slot(
            session_id=req.session_id,
            date=req.date,
            time=req.time,
        )

        if result.get("success"):
            appt.status = "booked"
            appt.confirmation_code = result.get("confirmation_code")
            appt.appointment_date = req.date
            appt.appointment_time = req.time
            appt.office_location = result.get("office")
        else:
            appt.status = "failed"
            appt.error_message = result.get("error", "Slot confirmation failed")

        db.commit()
        db.refresh(appt)

    except Exception as e:
        appt.status = "failed"
        appt.error_message = str(e)
        db.commit()
        db.refresh(appt)

    return AppointmentResponse(
        id=appt.id, service=appt.service, procedure_type=appt.procedure_type,
        status=appt.status, appointment_date=appt.appointment_date,
        appointment_time=appt.appointment_time, office_location=appt.office_location,
        confirmation_code=appt.confirmation_code, error_message=appt.error_message,
        created_at=appt.created_at, updated_at=appt.updated_at,
    )


# --- CAPTCHA relay endpoints ---

captcha_router = APIRouter(prefix="/api/captcha", tags=["captcha"])


@captcha_router.get("/pending")
async def get_pending_captcha(user: User = Depends(get_current_user)):
    """Check if there's a CAPTCHA waiting for this user."""
    from app.services.captcha_service import get_pending_for_chat
    if not user.telegram_chat_id:
        raise HTTPException(status_code=404, detail="No pending CAPTCHA")

    challenge = get_pending_for_chat(user.telegram_chat_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="No pending CAPTCHA")

    return CaptchaPendingResponse(
        captcha_id=challenge.captcha_id,
        image_url=f"data:image/png;base64,{challenge.image_base64}",
        captcha_type=challenge.captcha_type,
    )


@captcha_router.post("/solve")
async def solve_captcha(req: CaptchaSolveRequest, user: User = Depends(get_current_user)):
    """Submit CAPTCHA solution."""
    from app.services.captcha_service import submit_solution
    if not user.telegram_chat_id:
        raise HTTPException(status_code=400, detail="No Telegram chat linked")

    success = submit_solution(user.telegram_chat_id, req.solution)
    if not success:
        raise HTTPException(status_code=404, detail="No pending CAPTCHA for this session")

    return {"message": "Solution submitted"}
