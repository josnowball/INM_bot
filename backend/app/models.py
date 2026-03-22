import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base


def gen_id() -> str:
    return uuid.uuid4().hex


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    telegram_chat_id = Column(String, nullable=True, unique=True)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    """All PII fields are AES-256-GCM encrypted at rest."""
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)

    # Personal info (all encrypted)
    enc_first_name = Column(Text, nullable=True)
    enc_last_name = Column(Text, nullable=True)
    enc_middle_name = Column(Text, nullable=True)
    enc_nationality = Column(Text, nullable=True)
    enc_birth_date = Column(Text, nullable=True)  # ISO date string
    enc_birth_country = Column(Text, nullable=True)
    enc_birth_state = Column(Text, nullable=True)
    enc_gender = Column(Text, nullable=True)
    enc_marital_status = Column(Text, nullable=True)

    # Document info (encrypted)
    enc_passport_number = Column(Text, nullable=True)
    enc_passport_country = Column(Text, nullable=True)
    enc_passport_expiry = Column(Text, nullable=True)
    enc_curp = Column(Text, nullable=True)  # Mexican ID

    # Contact info (encrypted)
    enc_phone = Column(Text, nullable=True)
    enc_address_street = Column(Text, nullable=True)
    enc_address_city = Column(Text, nullable=True)
    enc_address_state = Column(Text, nullable=True)
    enc_address_zip = Column(Text, nullable=True)
    enc_address_country = Column(Text, nullable=True)

    # INM-specific (encrypted)
    enc_immigration_status = Column(Text, nullable=True)
    enc_entry_date = Column(Text, nullable=True)
    enc_permit_number = Column(Text, nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    service = Column(String, nullable=False)  # "inm" or "sre"
    procedure_type = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, in_progress, booked, failed
    appointment_date = Column(String, nullable=True)  # encrypted date once booked
    appointment_time = Column(String, nullable=True)
    office_location = Column(String, nullable=True)
    confirmation_code = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="appointments")


class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
