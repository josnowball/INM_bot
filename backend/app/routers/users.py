from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserProfile, EmailVerification
from app.schemas import (
    RegisterRequest, LoginRequest, TokenResponse,
    VerifyEmailRequest, ProfileUpdate, ProfileResponse, UserResponse,
)
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token, get_current_user
from app.encryption import encrypt, decrypt
from app.services.email_service import generate_code, send_verification_email

router = APIRouter(prefix="/api/auth", tags=["auth"])
profile_router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
    )
    db.add(user)
    db.flush()

    # Create empty profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)

    # Send verification email
    code = generate_code()
    verification = EmailVerification(
        user_id=user.id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=15),
    )
    db.add(verification)
    db.commit()

    await send_verification_email(req.email, code)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/verify-email")
async def verify_email(
    req: VerifyEmailRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verification = (
        db.query(EmailVerification)
        .filter(
            EmailVerification.user_id == user.id,
            EmailVerification.code == req.code,
            EmailVerification.used == False,
            EmailVerification.expires_at > datetime.utcnow(),
        )
        .first()
    )
    if not verification:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    verification.used = True
    user.email_verified = True
    db.commit()
    return {"message": "Email verified"}


@router.post("/resend-verification")
async def resend_verification(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.email_verified:
        return {"message": "Already verified"}

    code = generate_code()
    verification = EmailVerification(
        user_id=user.id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=15),
    )
    db.add(verification)
    db.commit()
    await send_verification_email(user.email, code)
    return {"message": "Verification code sent"}


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user


# --- Profile ---

def _decrypt_profile(profile: UserProfile) -> dict:
    """Decrypt all enc_ fields into a clean dict."""
    fields = {}
    for col in UserProfile.__table__.columns:
        if col.name.startswith("enc_"):
            clean_name = col.name[4:]  # strip "enc_"
            raw = getattr(profile, col.name)
            fields[clean_name] = decrypt(raw) if raw else None
    return fields


def _profile_completion(data: dict) -> int:
    """Calculate profile completion percentage."""
    required = [
        "first_name", "last_name", "nationality", "birth_date",
        "gender", "passport_number", "phone", "address_city",
    ]
    filled = sum(1 for k in required if data.get(k))
    return int((filled / len(required)) * 100)


@profile_router.get("/", response_model=ProfileResponse)
async def get_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        return ProfileResponse(completion_pct=0)

    data = _decrypt_profile(profile)
    data["completion_pct"] = _profile_completion(data)
    return ProfileResponse(**data)


@profile_router.put("/")
async def update_profile(
    req: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        enc_key = f"enc_{key}"
        if hasattr(profile, enc_key):
            setattr(profile, enc_key, encrypt(value) if value else None)

    db.commit()

    data = _decrypt_profile(profile)
    data["completion_pct"] = _profile_completion(data)
    return ProfileResponse(**data)
