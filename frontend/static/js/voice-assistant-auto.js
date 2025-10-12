/**
 * Auto-Playing Voice Assistant - Guides users through signup with TTS
 */

let currentAudio = null;
let hasPlayedWelcome = false;
let playedSections = new Set(); // Track which sections have been announced
let isAssistantSpeaking = false;

// Section mapping for scroll detection
const sectionAudioMap = {
    'section-1': 'welcome',
    'section-2': 'basic',
    'section-3': 'security',
    'section-4': 'address',
    'section-5': 'employment',
    'section-6': 'trusted',
    'section-7': 'review'
};

/**
 * Play voice assistant audio for a specific section
 */
async function playVoiceAssistant(section) {
    try {
        // Stop any currently playing audio
        if (currentAudio) {
            currentAudio.pause();
            currentAudio = null;
        }
        
        // Show speaking indicator
        showAssistantSpeaking(true);
        
        console.log(`Playing voice assistant for section: ${section}`);
        
        // Fetch audio from backend
        const audioUrl = `/api/voice-assistant/speak/${section}`;
        currentAudio = new Audio(audioUrl);
        
        // Handle audio events
        currentAudio.onplay = () => {
            isAssistantSpeaking = true;
            console.log('Voice assistant started speaking');
        };
        
        currentAudio.onended = () => {
            isAssistantSpeaking = false;
            showAssistantSpeaking(false);
            console.log('Voice assistant finished speaking');
            
            // After welcome, automatically play Basic Info instructions
            if (section === 'welcome') {
                console.log('Welcome finished. Playing Basic Info instructions in 1 second...');
                setTimeout(() => {
                    // Scroll to Basic Info section
                    scrollToSection('section-2');
                    playedSections.add('section-2'); // Mark as played
                    // Play audio after scroll
                    setTimeout(() => {
                        playVoiceAssistant('basic');
                    }, 500);
                }, 1000); // 1 second pause between sections
            }
            // Auto-trigger voice recording for all form sections
            else if (['basic', 'security', 'address', 'employment', 'trusted'].includes(section)) {
                console.log(`Starting auto-recording for ${section} section in 2 seconds...`);
                setTimeout(() => {
                    startAutoVoiceRecording(section);
                }, 2000); // 2 second delay as instructed in audio
            }
        };
        
        currentAudio.onerror = (error) => {
            isAssistantSpeaking = false;
            showAssistantSpeaking(false);
            console.error('Error playing voice assistant:', error);
        };
        
        // Play the audio
        await currentAudio.play();
        
    } catch (error) {
        console.error('Error in playVoiceAssistant:', error);
        showAssistantSpeaking(false);
        isAssistantSpeaking = false;
    }
}

/**
 * Show/hide visual indicator when assistant is speaking
 */
function showAssistantSpeaking(isSpeaking) {
    let indicator = document.getElementById('voice-assistant-indicator');
    
    if (!indicator && isSpeaking) {
        // Create indicator if it doesn't exist
        indicator = document.createElement('div');
        indicator.id = 'voice-assistant-indicator';
        indicator.className = 'voice-assistant-indicator';
        indicator.innerHTML = `
            <div class="assistant-avatar">
                <span class="assistant-icon">🎙️</span>
            </div>
            <div class="assistant-message">
                <strong>Voice Assistant</strong>
                <p>Speaking... Please listen</p>
            </div>
            <button class="btn-mute-assistant" onclick="muteAssistant()" title="Mute Assistant">
                🔇
            </button>
        `;
        document.body.appendChild(indicator);
    }
    
    if (indicator) {
        if (isSpeaking) {
            indicator.classList.add('active');
        } else {
            indicator.classList.remove('active');
        }
    }
}

/**
 * Mute/stop the voice assistant
 */
function muteAssistant() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    isAssistantSpeaking = false;
    showAssistantSpeaking(false);
}

/**
 * Start automatic voice recording with countdown timer
 */
async function startAutoVoiceRecording(section) {
    console.log(`Auto-starting voice recording for section: ${section}`);
    
    // Trigger the Filler Buddy button click
    await startVoiceFilling(section);
    
    // Show countdown timer
    let countdown = 30;
    const countdownInterval = setInterval(() => {
        countdown--;
        updateRecordingCountdown(section, countdown);
        
        if (countdown <= 0) {
            clearInterval(countdownInterval);
        }
    }, 1000);
    
    // Auto-stop recording after 30 seconds
    setTimeout(async () => {
        console.log('Auto-stopping voice recording after 30 seconds');
        stopVoiceRecording(section);
        
        // Wait for processing to complete, then check if we should auto-continue
        setTimeout(() => {
            checkAndAutoContinue(section);
        }, 3000); // Give 3 seconds for processing
    }, 30000); // 30 seconds
}

/**
 * Update recording countdown display
 */
function updateRecordingCountdown(section, seconds) {
    const statusId = section === 'basic' ? 'voiceStatus' : `voiceStatus${section.charAt(0).toUpperCase() + section.slice(1)}`;
    const statusDiv = document.getElementById(statusId);
    
    if (statusDiv) {
        const stopBtn = statusDiv.querySelector('.btn-stop-recording');
        if (stopBtn) {
            statusDiv.innerHTML = `
                <span class="status-text">🎤 Recording... (${seconds}s remaining)</span>
                <button type="button" class="btn-stop-recording" onclick="stopVoiceRecording('${section}')">Stop Now</button>
            `;
        }
    }
}

/**
 * Check if all required fields are filled and auto-continue
 */
function checkAndAutoContinue(section) {
    let allFieldsFilled = false;
    let nextSection = null;
    let nextSectionName = '';
    let currentSectionName = '';
    
    // Validate based on section
    if (section === 'basic') {
        currentSectionName = 'Basic Information';
        const firstName = document.getElementById('firstName').value.trim();
        const lastName = document.getElementById('lastName').value.trim();
        const email = document.getElementById('email').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        allFieldsFilled = firstName && lastName && email && phone && password && confirmPassword;
        nextSection = 'section-3';
        nextSectionName = 'Security Information';
        
    } else if (section === 'security') {
        currentSectionName = 'Security Information';
        const dob = document.getElementById('dob').value.trim();
        const ssn = document.getElementById('ssn').value.trim();
        const citizenYes = document.getElementById('citizen-yes');
        const citizenNo = document.getElementById('citizen-no');
        const citizenChecked = (citizenYes && citizenYes.checked) || (citizenNo && citizenNo.checked);
        
        allFieldsFilled = dob && ssn && citizenChecked;
        nextSection = 'section-4';
        nextSectionName = 'Address Information';
        
    } else if (section === 'address') {
        currentSectionName = 'Address Information';
        const address1 = document.getElementById('address1').value.trim();
        const city = document.getElementById('city').value.trim();
        const state = document.getElementById('state').value;
        const zipCode = document.getElementById('zipCode').value.trim();
        
        allFieldsFilled = address1 && city && state && zipCode;
        nextSection = 'section-5';
        nextSectionName = 'Employment Information';
        
    } else if (section === 'employment') {
        currentSectionName = 'Employment Information';
        const employmentStatus = document.getElementById('employmentStatus').value;
        
        allFieldsFilled = employmentStatus !== '';
        nextSection = 'section-6';
        nextSectionName = 'Trusted Contact';
        
    } else if (section === 'trusted') {
        currentSectionName = 'Trusted Contact';
        // Trusted contact is optional, so we can always continue
        allFieldsFilled = true;
        nextSection = 'section-7';
        nextSectionName = 'Review and Confirm';
    }
    
    console.log(`Checking ${currentSectionName} fields. All filled: ${allFieldsFilled}`);
    
    // Proceed based on validation
    if (allFieldsFilled) {
        console.log('All required fields filled! Auto-continuing to next section...');
        
        // Show success message
        showAutoProgressMessage(`✓ ${currentSectionName} complete! Moving to ${nextSectionName}...`);
        
        // Auto-scroll to next section and trigger audio
        setTimeout(() => {
            scrollToSection(nextSection);
            playedSections.delete(nextSection);
            
            // Trigger next section audio after scroll
            setTimeout(() => {
                const audioSectionMap = {
                    'section-3': 'security',
                    'section-4': 'address',
                    'section-5': 'employment',
                    'section-6': 'trusted',
                    'section-7': 'review'
                };
                const audioSection = audioSectionMap[nextSection];
                if (audioSection) {
                    playVoiceAssistant(audioSection);
                    playedSections.add(nextSection);
                }
            }, 1000);
        }, 2000);
    } else {
        console.log(`Some required fields missing in ${currentSectionName}. Retrying section...`);
        
        // Show retry message
        showAutoProgressMessage(`⚠ Missing required fields in ${currentSectionName}. Replaying instructions...`);
        
        // Replay the section audio and recording after 2 seconds
        setTimeout(() => {
            console.log(`Replaying ${currentSectionName} section...`);
            playVoiceAssistant(section);
        }, 2000);
    }
}

/**
 * Show auto-progress message
 */
function showAutoProgressMessage(message) {
    let messageDiv = document.getElementById('auto-progress-message');
    
    if (!messageDiv) {
        messageDiv = document.createElement('div');
        messageDiv.id = 'auto-progress-message';
        messageDiv.className = 'auto-progress-message';
        document.body.appendChild(messageDiv);
    }
    
    messageDiv.textContent = message;
    messageDiv.classList.add('show');
    
    setTimeout(() => {
        messageDiv.classList.remove('show');
    }, 4000);
}

/**
 * Initialize voice assistant on page load
 */
function initVoiceAssistant() {
    console.log('Initializing Voice Assistant...');
    
    // Play welcome message after a short delay
    setTimeout(() => {
        if (!hasPlayedWelcome) {
            playVoiceAssistant('welcome');
            hasPlayedWelcome = true;
            playedSections.add('section-1');
        }
    }, 1000); // 1 second delay after page load
    
    // Set up scroll listener to auto-play section instructions
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        // Debounce scroll events
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            checkSectionInView();
        }, 500);
    });
}

/**
 * Check which section is in view and play its audio if not played yet
 */
function checkSectionInView() {
    // Don't interrupt if assistant is currently speaking
    if (isAssistantSpeaking) {
        return;
    }
    
    const sections = document.querySelectorAll('.form-section');
    const scrollPosition = window.scrollY + 300; // Offset for better detection
    
    sections.forEach((section) => {
        const sectionTop = section.offsetTop;
        const sectionBottom = sectionTop + section.offsetHeight;
        const sectionId = section.id;
        
        // Check if section is in view
        if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
            // Check if we haven't played this section's audio yet
            if (!playedSections.has(sectionId) && sectionAudioMap[sectionId]) {
                playedSections.add(sectionId);
                const audioSection = sectionAudioMap[sectionId];
                
                // Add a small delay before playing
                setTimeout(() => {
                    playVoiceAssistant(audioSection);
                }, 500);
            }
        }
    });
}

/**
 * Replay current section's audio
 */
function replayCurrentSection() {
    const sections = document.querySelectorAll('.form-section');
    const scrollPosition = window.scrollY + 300;
    
    sections.forEach((section) => {
        const sectionTop = section.offsetTop;
        const sectionBottom = sectionTop + section.offsetHeight;
        const sectionId = section.id;
        
        if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
            if (sectionAudioMap[sectionId]) {
                playVoiceAssistant(sectionAudioMap[sectionId]);
            }
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initVoiceAssistant);
} else {
    initVoiceAssistant();
}

// Add CSS styles for the voice assistant indicator
const assistantStyles = document.createElement('style');
assistantStyles.textContent = `
    .voice-assistant-indicator {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
        display: none;
        align-items: center;
        gap: 1rem;
        z-index: 10000;
        max-width: 350px;
        animation: slideInRight 0.3s ease;
    }
    
    .voice-assistant-indicator.active {
        display: flex;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .assistant-avatar {
        width: 50px;
        height: 50px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    
    .assistant-icon {
        font-size: 1.8rem;
        animation: pulse-glow 2s infinite;
    }
    
    @keyframes pulse-glow {
        0%, 100% {
            transform: scale(1);
            filter: brightness(1);
        }
        50% {
            transform: scale(1.1);
            filter: brightness(1.3);
        }
    }
    
    .assistant-message {
        flex: 1;
    }
    
    .assistant-message strong {
        display: block;
        font-size: 0.95rem;
        margin-bottom: 0.25rem;
    }
    
    .assistant-message p {
        margin: 0;
        font-size: 0.85rem;
        opacity: 0.9;
    }
    
    .btn-mute-assistant {
        background: rgba(255, 255, 255, 0.2);
        border: none;
        color: white;
        font-size: 1.3rem;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        transition: all 0.3s ease;
        flex-shrink: 0;
    }
    
    .btn-mute-assistant:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: scale(1.1);
    }
    
    /* Auto-progress message */
    .auto-progress-message {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%) translateY(-100px);
        background: linear-gradient(135deg, #00d4aa 0%, #00a884 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 8px;
        box-shadow: 0 8px 30px rgba(0, 212, 170, 0.4);
        z-index: 10001;
        font-weight: 600;
        font-size: 1rem;
        transition: transform 0.3s ease;
        opacity: 0;
        pointer-events: none;
    }
    
    .auto-progress-message.show {
        transform: translateX(-50%) translateY(0);
        opacity: 1;
        pointer-events: auto;
        animation: slideDown 0.3s ease;
    }
    
    @keyframes slideDown {
        from {
            transform: translateX(-50%) translateY(-100px);
            opacity: 0;
        }
        to {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .voice-assistant-indicator {
            bottom: 10px;
            right: 10px;
            left: 10px;
            max-width: none;
            padding: 0.75rem 1rem;
        }
        
        .assistant-avatar {
            width: 40px;
            height: 40px;
        }
        
        .assistant-icon {
            font-size: 1.5rem;
        }
        
        .assistant-message strong {
            font-size: 0.85rem;
        }
        
        .assistant-message p {
            font-size: 0.75rem;
        }
        
        .auto-progress-message {
            padding: 0.75rem 1.5rem;
            font-size: 0.9rem;
        }
    }
`;
document.head.appendChild(assistantStyles);
