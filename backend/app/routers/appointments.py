from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserProfile, Appointment
from app.schemas import INMBookingRequest, SREBookingRequest, AppointmentResponse
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
