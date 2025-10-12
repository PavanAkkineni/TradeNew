"""
Database models and configuration for TradeCompass
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tradecompass.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Database dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Account type
    account_type = Column(String, nullable=False)  # 'stocks' (only type supported)


class UserProfile(Base):
    """User profile with detailed information"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Basic Information
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)
    preferred_name = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    
    # Security Information
    date_of_birth = Column(String, nullable=False)
    is_us_citizen = Column(Boolean, nullable=False)
    ssn_encrypted = Column(String, nullable=False)  # Encrypted SSN
    
    # Address Information
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    country = Column(String, default="USA")
    
    # Employment Information
    employment_status = Column(String, nullable=False)
    job_title = Column(String, nullable=True)
    employer_name = Column(String, nullable=True)
    
    # Investor Related Information
    works_at_financial_institution = Column(Boolean, default=False)
    financial_institution_name = Column(String, nullable=True)
    is_public_company_insider = Column(Boolean, default=False)
    public_company_name = Column(String, nullable=True)
    subject_to_backup_withholding = Column(Boolean, default=False)
    
    # Military Information
    has_military_experience = Column(Boolean, default=False)
    military_status = Column(String, nullable=True)
    military_branch = Column(String, nullable=True)
    military_rank = Column(String, nullable=True)
    
    # Trusted Contact (Optional)
    trusted_contact_name = Column(String, nullable=True)
    trusted_contact_email = Column(String, nullable=True)
    trusted_contact_phone = Column(String, nullable=True)
    trusted_contact_relationship = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSession(Base):
    """User session tracking"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    session_token = Column(String, unique=True, index=True, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)


class UserActivity(Base):
    """User activity log"""
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    activity_type = Column(String, nullable=False)  # login, logout, signup, etc.
    description = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
