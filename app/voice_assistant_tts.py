"""
Voice Assistant with Text-to-Speech - Guides users through signup process
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from gtts import gTTS
import io
import logging

logger = logging.getLogger(__name__)

# Router setup
router = APIRouter(prefix="/api/voice-assistant", tags=["voice-assistant"])

# Section-specific prompts
SECTION_PROMPTS = {
    'welcome': """
        Welcome to TradeCompass! I'm your voice assistant, and I'll be helping you create your account today. 
        explaining what information is needed. After each section's audio instruction, 
        please wait 2 seconds and speak your answers. 
        Let's begin!
    """,
    
    'basic': """
        Now we're in the Basic Information section. 
        I'll need you to provide the following information:
        First, your First Name.
        Then your Last Name.
        Your Email Address.
        Your Mobile Number.
        A secure Password
        Please Confirm your Password by entering it again.
        And finally, let me know if you have any Military Experience.
        
        Please wait 2 seconds after this audio stops. Recording will start automatically and last for 30 seconds.
        Speak all your information clearly. For example, you can say:
        My first name is John, last name is Doe, 
        If any required fields are missing, I'll replay these instructions so you can try again.
    """,
    
    'security': """
        Great! Now we're in the Security Information section. This is step 3 of 7.
        For regulatory compliance, I need:
        Your Date of Birth.
        Whether you're a U.S. Citizen.
        And your Social Security Number.
        
        Wait 2 seconds after this audio stops. Recording will start automatically and last for 30 seconds.
        For example: My date of birth is January 15, 1990, I am a U.S. citizen, 
        
        If any required fields are missing, I'll replay these instructions so you can try again.
    """,
    
    'address': """
        Moving on to Address Information. This is step 4 of 7.
        Please provide:
        Your Street Address.
        Apartment or Suite number if applicable.
        Your City.
        Your State.
        And your ZIP Code.
        
        Wait 2 seconds. Recording will start automatically and last for 30 seconds..
        
        If any required fields are missing, I'll replay these instructions so you can try again.
    """,
    
    'employment': """
        Now for Employment Information. This is step 5 of 7.
        I need to know:
        Your Employment Status, whether you're employed, unemployed, a student, or retired.
        If employed, your Employer's Name.
        Your Job Title or Occupation.
        And whether you're an insider of a publicly traded company.
        
        Wait 2 seconds. Recording will start automatically and last for 30 seconds.
        For example: I am employed at Tech Corp as a Software Engineer, and I am not a public company insider.
        
        If any required fields are missing, I'll replay these instructions so you can try again.
    """,
    
    'trusted': """
        This is the Trusted Contact Person section. This is step 6 of 7, and it's optional.
        If you'd like to designate someone we can contact if we're unable to reach you, please provide:
        Their Full Name.
        Their Email Address.
        Their Phone Number.
        And their Relationship to you.
        
        Wait 2 seconds. Recording will start automatically and last for 30 seconds.
        For example: My trusted contact is Jane Smith, her email is jane at example dot com, 
        phone number is 555-1234, and she is my spouse.
        
        Since this section is optional, you can say 'skip' or remain silent if you don't want to add a trusted contact.
    """,
    
    'review': """
        Excellent! We've reached the final step, Review and Confirm. This is step 7 of 7.
        Please take a moment to review all the information you've provided.
        Make sure everything is correct. If you need to make any changes, 
        you can scroll back to the relevant section.
        When you're ready, check all the agreement boxes and click Submit Account to complete your registration.
        Thank you for choosing TradeCompass!
    """
}


@router.get("/speak/{section}")
async def speak_section_instructions(section: str):
    """
    Generate and return audio speech for a specific section
    
    Args:
        section: Section name (welcome, basic, security, address, employment, trusted, review)
    
    Returns:
        Audio stream in MP3 format
    """
    try:
        # Validate section
        if section not in SECTION_PROMPTS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid section. Valid sections: {', '.join(SECTION_PROMPTS.keys())}"
            )
        
        # Get the prompt text
        prompt_text = SECTION_PROMPTS[section].strip()
        
        logger.info(f"Generating speech for section: {section}")
        
        # Generate speech using gTTS
        tts = gTTS(text=prompt_text, lang='en', slow=False)
        
        # Save to BytesIO buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # Return as streaming response
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"inline; filename=voice_{section}.mp3",
                "Cache-Control": "no-cache"
            }
        )
    
    except Exception as e:
        logger.error(f"Error generating speech for section {section}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech: {str(e)}"
        )


@router.get("/sections")
async def get_available_sections():
    """Get list of available sections with voice instructions"""
    return {
        "sections": list(SECTION_PROMPTS.keys()),
        "total": len(SECTION_PROMPTS)
    }
