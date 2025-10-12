/**
 * Voice Form Filler - Record audio and auto-fill form fields using AI
 */

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let currentSection = 'basic'; // Track which section is being filled

/**
 * Start voice recording for form filling
 * @param {string} section - Section type: 'basic', 'security', or 'address'
 */
async function startVoiceFilling(section = 'basic') {
    try {
        // Request microphone permission
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Initialize media recorder
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        // Collect audio data
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        
        // Handle recording stop
        mediaRecorder.onstop = async () => {
            await processRecordedAudio();
            // Stop all tracks to release microphone
            stream.getTracks().forEach(track => track.stop());
        };
        
        // Start recording
        mediaRecorder.start();
        isRecording = true;
        currentSection = section;
        
        // Update UI based on section
        const btnId = section === 'basic' ? 'voiceFillerBtn' : `voiceFillerBtn${section.charAt(0).toUpperCase() + section.slice(1)}`;
        const statusId = section === 'basic' ? 'voiceStatus' : `voiceStatus${section.charAt(0).toUpperCase() + section.slice(1)}`;
        
        document.getElementById(btnId).disabled = true;
        document.getElementById(statusId).style.display = 'flex';
        
        console.log('Voice recording started...');
        
    } catch (error) {
        console.error('Error starting voice recording:', error);
        showVoiceError('Could not access microphone. Please allow microphone access.');
    }
}

/**
 * Stop voice recording
 * @param {string} section - Section type: 'basic', 'security', or 'address'
 */
function stopVoiceRecording(section = 'basic') {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        currentSection = section;
        
        // Update UI based on section
        const statusId = section === 'basic' ? 'voiceStatus' : `voiceStatus${section.charAt(0).toUpperCase() + section.slice(1)}`;
        document.getElementById(statusId).innerHTML = '<span class="status-text">Processing...</span>';
        
        console.log('Voice recording stopped. Processing...');
    }
}

/**
 * Process recorded audio and send to backend
 */
async function processRecordedAudio() {
    try {
        // Create audio blob from chunks
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        
        console.log(`Audio recorded: ${audioBlob.size} bytes, type: ${audioBlob.type}`);
        
        // Create form data
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        
        // Determine endpoint based on current section
        const endpoints = {
            'basic': '/api/voice/fill-basic-info',
            'security': '/api/voice/fill-security-info',
            'address': '/api/voice/fill-address-info',
            'employment': '/api/voice/fill-employment-info',
            'trusted': '/api/voice/fill-trusted-contact'
        };
        const endpoint = endpoints[currentSection] || endpoints['basic'];
        
        // Send to backend
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to process audio');
        }
        
        const result = await response.json();
        console.log('Voice processing result:', result);
        
        if (result.success && result.data) {
            // Auto-fill form fields based on section
            if (currentSection === 'basic') {
                fillBasicInfoFields(result.data);
            } else if (currentSection === 'security') {
                fillSecurityInfoFields(result.data);
            } else if (currentSection === 'address') {
                fillAddressInfoFields(result.data);
            } else if (currentSection === 'employment') {
                fillEmploymentInfoFields(result.data);
            } else if (currentSection === 'trusted') {
                fillTrustedContactFields(result.data);
            }
            showVoiceSuccess('Form filled successfully from your voice!', currentSection);
        } else {
            throw new Error('No data extracted from audio');
        }
        
    } catch (error) {
        console.error('Error processing audio:', error);
        showVoiceError(`Error: ${error.message}`, currentSection);
    } finally {
        // Reset UI
        resetVoiceUI(currentSection);
    }
}

/**
 * Fill basic info form fields with extracted data
 */
function fillBasicInfoFields(data) {
    console.log('Filling form with data:', data);
    
    // Map of data keys to form field IDs
    const fieldMapping = {
        firstName: 'firstName',
        middleName: 'middleName',
        lastName: 'lastName',
        preferredName: 'preferredName',
        email: 'email',
        phone: 'phone',
        password: 'password',
        confirmPassword: 'confirmPassword',
        militaryStatus: 'militaryStatus',
        militaryBranch: 'militaryBranch',
        militaryRank: 'militaryRank'
    };
    
    // Fill each field if data exists
    Object.keys(fieldMapping).forEach(key => {
        if (data[key]) {
            const fieldId = fieldMapping[key];
            const field = document.getElementById(fieldId);
            if (field) {
                field.value = data[key];
                // Add a visual effect to show the field was filled
                field.classList.add('field-auto-filled');
                setTimeout(() => field.classList.remove('field-auto-filled'), 2000);
            }
        }
    });
    
    // Handle military experience radio buttons
    if (data.military) {
        const militaryValue = data.military.toLowerCase();
        if (militaryValue === 'yes') {
            document.getElementById('military-yes').checked = true;
            toggleMilitary(true);
        } else if (militaryValue === 'no') {
            document.getElementById('military-no').checked = true;
            toggleMilitary(false);
        }
    }
}

/**
 * Fill security info form fields with extracted data
 */
function fillSecurityInfoFields(data) {
    console.log('Filling security form with data:', data);
    
    // Fill date of birth
    if (data.dob) {
        const dobField = document.getElementById('dob');
        if (dobField) {
            dobField.value = data.dob;
            dobField.classList.add('field-auto-filled');
            setTimeout(() => dobField.classList.remove('field-auto-filled'), 2000);
        }
    }
    
    // Fill U.S. citizen radio
    if (data.citizen) {
        const citizenValue = data.citizen.toLowerCase();
        if (citizenValue === 'yes') {
            document.getElementById('citizen-yes').checked = true;
        } else if (citizenValue === 'no') {
            document.getElementById('citizen-no').checked = true;
        }
    }
    
    // Fill SSN
    if (data.ssn) {
        const ssnField = document.getElementById('ssn');
        if (ssnField) {
            ssnField.value = data.ssn;
            ssnField.classList.add('field-auto-filled');
            setTimeout(() => ssnField.classList.remove('field-auto-filled'), 2000);
        }
    }
}

/**
 * Fill address info form fields with extracted data
 */
function fillAddressInfoFields(data) {
    console.log('Filling address form with data:', data);
    
    const fieldMapping = {
        address1: 'address1',
        address2: 'address2',
        city: 'city',
        state: 'state',
        zipCode: 'zipCode'
    };
    
    // Fill each field if data exists
    Object.keys(fieldMapping).forEach(key => {
        if (data[key]) {
            const fieldId = fieldMapping[key];
            const field = document.getElementById(fieldId);
            if (field) {
                field.value = data[key];
                field.classList.add('field-auto-filled');
                setTimeout(() => field.classList.remove('field-auto-filled'), 2000);
            }
        }
    });
}

/**
 * Fill employment info form fields with extracted data
 */
function fillEmploymentInfoFields(data) {
    console.log('Filling employment form with data:', data);
    
    // Fill employment status dropdown
    if (data.employmentStatus) {
        const statusField = document.getElementById('employmentStatus');
        if (statusField) {
            statusField.value = data.employmentStatus.toLowerCase();
            statusField.classList.add('field-auto-filled');
            setTimeout(() => statusField.classList.remove('field-auto-filled'), 2000);
            
            // Trigger the change event to show employment details if employed
            if (data.employmentStatus.toLowerCase() === 'employed' || data.employmentStatus.toLowerCase() === 'self-employed') {
                toggleEmploymentFields();
            }
        }
    }
    
    // Fill employer name (mapped to employerName field)
    if (data.employer) {
        const employerField = document.getElementById('employerName');
        if (employerField) {
            employerField.value = data.employer;
            employerField.classList.add('field-auto-filled');
            setTimeout(() => employerField.classList.remove('field-auto-filled'), 2000);
        }
    }
    
    // Fill occupation/job title
    if (data.occupation) {
        const jobTitleField = document.getElementById('jobTitle');
        if (jobTitleField) {
            jobTitleField.value = data.occupation;
            jobTitleField.classList.add('field-auto-filled');
            setTimeout(() => jobTitleField.classList.remove('field-auto-filled'), 2000);
        }
    }
    
    // Fill public company insider radio
    if (data.insider) {
        const insiderValue = data.insider.toLowerCase();
        if (insiderValue === 'yes') {
            const insiderYes = document.getElementById('insider-yes');
            if (insiderYes) insiderYes.checked = true;
        } else if (insiderValue === 'no') {
            const insiderNo = document.getElementById('insider-no');
            if (insiderNo) insiderNo.checked = true;
        }
    }
}

/**
 * Fill trusted contact form fields with extracted data
 */
function fillTrustedContactFields(data) {
    console.log('Filling trusted contact form with data:', data);
    
    const fieldMapping = {
        trustedName: 'trustedName',
        trustedEmail: 'trustedEmail',
        trustedPhone: 'trustedPhone',
        trustedRelationship: 'trustedRelationship'
    };
    
    // Fill each field if data exists
    Object.keys(fieldMapping).forEach(key => {
        if (data[key]) {
            const fieldId = fieldMapping[key];
            const field = document.getElementById(fieldId);
            if (field) {
                field.value = data[key];
                field.classList.add('field-auto-filled');
                setTimeout(() => field.classList.remove('field-auto-filled'), 2000);
            }
        }
    });
}

/**
 * Reset voice UI to initial state
 * @param {string} section - Section type: 'basic', 'security', 'address', 'employment', or 'trusted'
 */
function resetVoiceUI(section = 'basic') {
    const btnId = section === 'basic' ? 'voiceFillerBtn' : `voiceFillerBtn${section.charAt(0).toUpperCase() + section.slice(1)}`;
    const statusId = section === 'basic' ? 'voiceStatus' : `voiceStatus${section.charAt(0).toUpperCase() + section.slice(1)}`;
    
    document.getElementById(btnId).disabled = false;
    document.getElementById(statusId).style.display = 'none';
    
    const stopBtnOnclick = section === 'basic' ? "stopVoiceRecording()" : `stopVoiceRecording('${section}')`;
    document.getElementById(statusId).innerHTML = `<span class="status-text">Recording...</span><button type="button" class="btn-stop-recording" onclick="${stopBtnOnclick}">Stop</button>`;
    audioChunks = [];
}

/**
 * Show success message
 * @param {string} message - Success message to display
 * @param {string} section - Section type: 'basic', 'security', or 'address'
 */
function showVoiceSuccess(message, section = 'basic') {
    const statusId = section === 'basic' ? 'voiceStatus' : `voiceStatus${section.charAt(0).toUpperCase() + section.slice(1)}`;
    const statusDiv = document.getElementById(statusId);
    statusDiv.innerHTML = `<span class="status-text success">✓ ${message}</span>`;
    statusDiv.style.display = 'flex';
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 3000);
}

/**
 * Show error message
 * @param {string} message - Error message to display
 * @param {string} section - Section type: 'basic', 'security', or 'address'
 */
function showVoiceError(message, section = 'basic') {
    const statusId = section === 'basic' ? 'voiceStatus' : `voiceStatus${section.charAt(0).toUpperCase() + section.slice(1)}`;
    const statusDiv = document.getElementById(statusId);
    statusDiv.innerHTML = `<span class="status-text error">✗ ${message}</span>`;
    statusDiv.style.display = 'flex';
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
}

// Add visual feedback styles for auto-filled fields
const style = document.createElement('style');
style.textContent = `
    .field-auto-filled {
        animation: highlightField 2s ease;
    }
    
    @keyframes highlightField {
        0% { background-color: rgba(0, 212, 170, 0.1); }
        100% { background-color: transparent; }
    }
`;
document.head.appendChild(style);
