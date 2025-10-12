"""
Voice Form Filler - Uses Gemini API to extract form data from voice input
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Router setup
router = APIRouter(prefix="/api/voice", tags=["voice"])

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyAiNYDmMsmYThgrmh0qAYMu3qbm-HRiD9w"

class VoiceFormData(BaseModel):
    """Structured form data extracted from voice"""
    firstName: Optional[str] = None
    middleName: Optional[str] = None
    lastName: Optional[str] = None
    preferredName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    confirmPassword: Optional[str] = None
    military: Optional[str] = None  # "yes" or "no"
    militaryStatus: Optional[str] = None
    militaryBranch: Optional[str] = None
    militaryRank: Optional[str] = None


class VoiceSecurityData(BaseModel):
    """Security information extracted from voice"""
    dob: Optional[str] = None  # Date of birth in YYYY-MM-DD format
    citizen: Optional[str] = None  # "yes" or "no"
    ssn: Optional[str] = None  # Social Security Number


class VoiceAddressData(BaseModel):
    """Address information extracted from voice"""
    address1: Optional[str] = None  # Street address
    address2: Optional[str] = None  # Apartment, suite, etc.
    city: Optional[str] = None
    state: Optional[str] = None  # Two-letter state code (e.g., "CA", "NY")
    zipCode: Optional[str] = None


class VoiceEmploymentData(BaseModel):
    """Employment information extracted from voice"""
    employmentStatus: Optional[str] = None  # "employed", "unemployed", "student", "retired"
    employer: Optional[str] = None
    occupation: Optional[str] = None
    insider: Optional[str] = None  # "yes" or "no" - public company insider


class VoiceTrustedContactData(BaseModel):
    """Trusted contact information extracted from voice"""
    trustedName: Optional[str] = None
    trustedEmail: Optional[str] = None
    trustedPhone: Optional[str] = None
    trustedRelationship: Optional[str] = None


def get_gemini_client():
    """Initialize and return Gemini client"""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize AI service")


async def process_audio_with_gemini(audio_bytes: bytes, mime_type: str) -> Dict[str, Any]:
    """
    Process audio using Gemini API and extract structured form data
    
    Args:
        audio_bytes: Raw audio data
        mime_type: Audio MIME type (e.g., 'audio/mp3', 'audio/webm', 'audio/wav')
    
    Returns:
        Dictionary with extracted form fields
    """
    try:
        client = get_gemini_client()
        
        # Construct the prompt for Gemini
        prompt = """
        Listen to this audio carefully and extract personal information for a signup form.
        
        Extract the following fields if mentioned:
        - First Name (firstName)
        - Middle Name (middleName) 
        - Last Name (lastName)
        - Preferred Name (preferredName)
        - Email Address (email)
        - Mobile Number (phone)
        - Password (password)
        - Confirm Password (confirmPassword)
        - Military Experience (military) - answer "yes" or "no"
        - Military Status (militaryStatus) - if mentioned: "serving", "transitioning", or "post"
        - Military Branch (militaryBranch) - if mentioned: "army", "marines", "navy", "airforce", "spaceforce", "coastguard"
        - Military Rank (militaryRank) - if mentioned
        
        Return ONLY a valid JSON object with the extracted fields. Use null for fields not mentioned.
        Do not include any other text, explanation, or markdown formatting.
        
        Example format:
        {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "Pass123",
            "confirmPassword": "Pass123",
            "military": "no"
        }
        """
        
        # Generate content with audio
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=mime_type
                )
            ]
        )
        
        # Extract and parse the response
        response_text = response.text.strip()
        logger.info(f"Gemini response: {response_text}")
        
        # Try to parse as JSON
        try:
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            form_data = json.loads(response_text)
            return form_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Response text: {response_text}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to extract structured data from audio"
            )
    
    except Exception as e:
        logger.error(f"Error processing audio with Gemini: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process audio: {str(e)}"
        )


@router.post("/fill-basic-info", response_model=Dict[str, Any])
async def fill_basic_info_from_voice(
    audio: UploadFile = File(..., description="Audio file with form information")
):
    """
    Process voice audio to extract and return Basic Info form fields
    
    Accepts audio in MP3, WAV, WebM, or OGG format
    Returns structured JSON with form field values
    """
    try:
        # Validate file type
        allowed_types = ['audio/mp3', 'audio/mpeg', 'audio/wav', 'audio/webm', 'audio/ogg']
        if audio.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read audio data
        audio_bytes = await audio.read()
        
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        logger.info(f"Processing audio file: {audio.filename}, size: {len(audio_bytes)} bytes, type: {audio.content_type}")
        
        # Process with Gemini
        form_data = await process_audio_with_gemini(audio_bytes, audio.content_type)
        
        return {
            "success": True,
            "data": form_data,
            "message": "Form data extracted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in fill_basic_info_from_voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fill-security-info", response_model=Dict[str, Any])
async def fill_security_info_from_voice(
    audio: UploadFile = File(..., description="Audio file with security information")
):
    """
    Process voice audio to extract and return Security Information form fields
    
    Accepts audio in MP3, WAV, WebM, or OGG format
    Returns structured JSON with security field values
    """
    try:
        # Validate file type
        allowed_types = ['audio/mp3', 'audio/mpeg', 'audio/wav', 'audio/webm', 'audio/ogg']
        if audio.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read audio data
        audio_bytes = await audio.read()
        
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        logger.info(f"Processing security info audio: {audio.filename}, size: {len(audio_bytes)} bytes")
        
        # Custom prompt for security information
        prompt = """
        Listen to this audio carefully and extract security information for a signup form.
        
        Extract the following fields if mentioned:
        - Date of Birth (dob) - format as YYYY-MM-DD (e.g., "1990-05-15")
        - U.S. Citizen (citizen) - answer "yes" or "no"
        - Social Security Number (ssn) - format with dashes XXX-XX-XXXX (e.g., "123-45-6789")
        
        Return ONLY a valid JSON object with the extracted fields. Use null for fields not mentioned.
        Do not include any other text, explanation, or markdown formatting.
        
        Example format:
        {
            "dob": "1990-05-15",
            "citizen": "yes",
            "ssn": "123-45-6789"
        }
        """
        
        # Process with Gemini using custom prompt
        client = get_gemini_client()
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=audio.content_type
                )
            ]
        )
        
        response_text = response.text.strip()
        logger.info(f"Gemini response for security: {response_text}")
        
        # Parse JSON
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        form_data = json.loads(response_text)
        
        return {
            "success": True,
            "data": form_data,
            "message": "Security information extracted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in fill_security_info_from_voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fill-address-info", response_model=Dict[str, Any])
async def fill_address_info_from_voice(
    audio: UploadFile = File(..., description="Audio file with address information")
):
    """
    Process voice audio to extract and return Address Information form fields
    
    Accepts audio in MP3, WAV, WebM, or OGG format
    Returns structured JSON with address field values
    """
    try:
        # Validate file type
        allowed_types = ['audio/mp3', 'audio/mpeg', 'audio/wav', 'audio/webm', 'audio/ogg']
        if audio.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read audio data
        audio_bytes = await audio.read()
        
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        logger.info(f"Processing address info audio: {audio.filename}, size: {len(audio_bytes)} bytes")
        
        # Custom prompt for address information
        prompt = """
        Listen to this audio carefully and extract address information for a signup form.
        
        Extract the following fields if mentioned:
        - Street Address (address1) - full street address
        - Apartment/Suite (address2) - apartment, suite, unit number if mentioned
        - City (city)
        - State (state) - use TWO-LETTER state code (e.g., "CA" for California, "NY" for New York, "TX" for Texas)
        - ZIP Code (zipCode) - 5 digit zip code
        
        Return ONLY a valid JSON object with the extracted fields. Use null for fields not mentioned.
        Do not include any other text, explanation, or markdown formatting.
        
        Important: State must be a two-letter abbreviation (AL, AK, AZ, AR, CA, CO, CT, DE, FL, GA, HI, ID, IL, IN, IA, KS, KY, LA, ME, MD, MA, MI, MN, MS, MO, MT, NE, NV, NH, NJ, NM, NY, NC, ND, OH, OK, OR, PA, RI, SC, SD, TN, TX, UT, VT, VA, WA, WV, WI, WY)
        
        Example format:
        {
            "address1": "123 Main Street",
            "address2": "Apt 4B",
            "city": "Los Angeles",
            "state": "CA",
            "zipCode": "90001"
        }
        """
        
        # Process with Gemini using custom prompt
        client = get_gemini_client()
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=audio.content_type
                )
            ]
        )
        
        response_text = response.text.strip()
        logger.info(f"Gemini response for address: {response_text}")
        
        # Parse JSON
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        form_data = json.loads(response_text)
        
        return {
            "success": True,
            "data": form_data,
            "message": "Address information extracted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in fill_address_info_from_voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fill-employment-info", response_model=Dict[str, Any])
async def fill_employment_info_from_voice(
    audio: UploadFile = File(..., description="Audio file with employment information")
):
    """
    Process voice audio to extract and return Employment Information form fields
    
    Accepts audio in MP3, WAV, WebM, or OGG format
    Returns structured JSON with employment field values
    """
    try:
        # Validate file type
        allowed_types = ['audio/mp3', 'audio/mpeg', 'audio/wav', 'audio/webm', 'audio/ogg']
        if audio.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read audio data
        audio_bytes = await audio.read()
        
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        logger.info(f"Processing employment info audio: {audio.filename}, size: {len(audio_bytes)} bytes")
        
        # Custom prompt for employment information
        prompt = """
        Listen to this audio carefully and extract employment information for a signup form.
        
        Extract the following fields if mentioned:
        - Employment Status (employmentStatus) - use one of: "employed", "unemployed", "student", "retired"
        - Employer (employer) - company name if employed
        - Occupation (occupation) - job title or role
        - Public Company Insider (insider) - answer "yes" or "no" (are you an insider of a publicly traded company)
        
        Return ONLY a valid JSON object with the extracted fields. Use null for fields not mentioned.
        Do not include any other text, explanation, or markdown formatting.
        
        Example format:
        {
            "employmentStatus": "employed",
            "employer": "Tech Corp",
            "occupation": "Software Engineer",
            "insider": "no"
        }
        """
        
        # Process with Gemini using custom prompt
        client = get_gemini_client()
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=audio.content_type
                )
            ]
        )
        
        response_text = response.text.strip()
        logger.info(f"Gemini response for employment: {response_text}")
        
        # Parse JSON
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        form_data = json.loads(response_text)
        
        return {
            "success": True,
            "data": form_data,
            "message": "Employment information extracted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in fill_employment_info_from_voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fill-trusted-contact", response_model=Dict[str, Any])
async def fill_trusted_contact_from_voice(
    audio: UploadFile = File(..., description="Audio file with trusted contact information")
):
    """
    Process voice audio to extract and return Trusted Contact form fields
    
    Accepts audio in MP3, WAV, WebM, or OGG format
    Returns structured JSON with trusted contact field values
    """
    try:
        # Validate file type
        allowed_types = ['audio/mp3', 'audio/mpeg', 'audio/wav', 'audio/webm', 'audio/ogg']
        if audio.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read audio data
        audio_bytes = await audio.read()
        
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        logger.info(f"Processing trusted contact audio: {audio.filename}, size: {len(audio_bytes)} bytes")
        
        # Custom prompt for trusted contact information
        prompt = """
        Listen to this audio carefully and extract trusted contact person information for a signup form.
        
        Extract the following fields if mentioned:
        - Trusted Contact Name (trustedName) - full name
        - Trusted Contact Email (trustedEmail) - email address
        - Trusted Contact Phone (trustedPhone) - phone number
        - Relationship (trustedRelationship) - relationship to the user (e.g., "parent", "spouse", "friend", "sibling")
        
        Return ONLY a valid JSON object with the extracted fields. Use null for fields not mentioned.
        Do not include any other text, explanation, or markdown formatting.
        
        Example format:
        {
            "trustedName": "Jane Smith",
            "trustedEmail": "jane@example.com",
            "trustedPhone": "555-1234",
            "trustedRelationship": "spouse"
        }
        """
        
        # Process with Gemini using custom prompt
        client = get_gemini_client()
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=audio.content_type
                )
            ]
        )
        
        response_text = response.text.strip()
        logger.info(f"Gemini response for trusted contact: {response_text}")
        
        # Parse JSON
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        form_data = json.loads(response_text)
        
        return {
            "success": True,
            "data": form_data,
            "message": "Trusted contact information extracted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in fill_trusted_contact_from_voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_voice_endpoint():
    """Test endpoint to verify voice API is working"""
    return {
        "status": "ok",
        "message": "Voice form filler API is running",
        "gemini_configured": GEMINI_API_KEY is not None
    }
