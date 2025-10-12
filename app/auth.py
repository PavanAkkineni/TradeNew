"""
Authentication and user management for TradeCompass
"""
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import secrets
import os
import hashlib

from app.database import User, UserProfile, UserSession, UserActivity

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Encryption key for sensitive data (SSN)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)


def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    if not password:
        raise ValueError("Password cannot be empty")
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    if not plain_password:
        return False
    return hash_password(plain_password) == hashed_password


def encrypt_ssn(ssn: str) -> str:
    """Encrypt SSN for secure storage"""
    return cipher_suite.encrypt(ssn.encode()).decode()


def decrypt_ssn(encrypted_ssn: str) -> str:
    """Decrypt SSN"""
    return cipher_suite.decrypt(encrypted_ssn.encode()).decode()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, password: str, account_type: str) -> User:
    """Create a new user"""
    hashed_password = hash_password(password)
    
    user = User(
        email=email,
        hashed_password=hashed_password,
        account_type=account_type,
        is_active=True,
        is_verified=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log activity
    log_activity(db, user.id, "signup", f"User registered with email: {email}")
    
    return user


def create_user_profile(db: Session, user_id: int, profile_data: dict) -> UserProfile:
    """Create user profile with detailed information"""
    
    # Encrypt SSN
    encrypted_ssn = encrypt_ssn(profile_data.get("ssn", ""))
    
    profile = UserProfile(
        user_id=user_id,
        first_name=profile_data.get("first_name"),
        middle_name=profile_data.get("middle_name"),
        last_name=profile_data.get("last_name"),
        preferred_name=profile_data.get("preferred_name"),
        phone=profile_data.get("phone"),
        date_of_birth=profile_data.get("date_of_birth"),
        is_us_citizen=profile_data.get("is_us_citizen", True),
        ssn_encrypted=encrypted_ssn,
        address_line1=profile_data.get("address_line1"),
        address_line2=profile_data.get("address_line2"),
        city=profile_data.get("city"),
        state=profile_data.get("state"),
        zip_code=profile_data.get("zip_code"),
        country=profile_data.get("country", "USA"),
        employment_status=profile_data.get("employment_status"),
        job_title=profile_data.get("job_title"),
        employer_name=profile_data.get("employer_name"),
        works_at_financial_institution=profile_data.get("works_at_financial_institution", False),
        financial_institution_name=profile_data.get("financial_institution_name"),
        is_public_company_insider=profile_data.get("is_public_company_insider", False),
        public_company_name=profile_data.get("public_company_name"),
        subject_to_backup_withholding=profile_data.get("subject_to_backup_withholding", False),
        has_military_experience=profile_data.get("has_military_experience", False),
        military_status=profile_data.get("military_status"),
        military_branch=profile_data.get("military_branch"),
        military_rank=profile_data.get("military_rank"),
        trusted_contact_name=profile_data.get("trusted_contact_name"),
        trusted_contact_email=profile_data.get("trusted_contact_email"),
        trusted_contact_phone=profile_data.get("trusted_contact_phone"),
        trusted_contact_relationship=profile_data.get("trusted_contact_relationship")
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Log activity
    log_activity(db, user.id, "login", f"User logged in: {email}")
    
    return user


def create_session(db: Session, user_id: int, ip_address: str = None, user_agent: str = None) -> UserSession:
    """Create a new user session"""
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    session = UserSession(
        user_id=user_id,
        session_token=session_token,
        ip_address=ip_address,
        user_agent=user_agent,
        is_active=True,
        expires_at=expires_at
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


def get_session(db: Session, session_token: str) -> Optional[UserSession]:
    """Get session by token"""
    session = db.query(UserSession).filter(
        UserSession.session_token == session_token,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    return session


def invalidate_session(db: Session, session_token: str) -> bool:
    """Invalidate a session (logout)"""
    session = db.query(UserSession).filter(UserSession.session_token == session_token).first()
    if session:
        session.is_active = False
        db.commit()
        return True
    return False


def log_activity(db: Session, user_id: int, activity_type: str, description: str = None, ip_address: str = None):
    """Log user activity"""
    activity = UserActivity(
        user_id=user_id,
        activity_type=activity_type,
        description=description,
        ip_address=ip_address
    )
    
    db.add(activity)
    db.commit()


def get_user_profile(db: Session, user_id: int) -> Optional[UserProfile]:
    """Get user profile by user ID"""
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()


def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str):
    """Validate password - just check if it's not empty"""
    if not password or password.strip() == "":
        return False, "Password cannot be empty"
    return True, "Password is valid"
