// Signup Form JavaScript
let currentStep = 1;
const totalSteps = 7;
let formData = {
    accountType: 'stocks',  // Default to stocks account
    profile: {}
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check for account type from URL
    const urlParams = new URLSearchParams(window.location.search);
    const accountType = urlParams.get('type');
    if (accountType) {
        selectAccountType(accountType);
    }
    
    // Setup account type cards
    document.querySelectorAll('.account-type-card').forEach(card => {
        card.addEventListener('click', function() {
            const type = this.getAttribute('data-type');
            selectAccountType(type);
        });
    });
    
    // Setup radio option clicks
    document.querySelectorAll('.radio-option').forEach(option => {
        option.addEventListener('click', function() {
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
                // Remove selected class from siblings
                this.parentElement.querySelectorAll('.radio-option').forEach(opt => {
                    opt.classList.remove('selected');
                });
                this.classList.add('selected');
            }
        });
    });
});

function selectAccountType(type) {
    // Remove selected class from all cards
    document.querySelectorAll('.account-type-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selected class to clicked card
    const selectedCard = document.querySelector(`.account-type-card[data-type="${type}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
        formData.accountType = type;
        document.getElementById('btn-1').disabled = false;
    }
}

function nextSection() {
    // Validate current section
    if (!validateSection(currentStep)) {
        return;
    }
    
    // Save data from current section
    saveSectionData(currentStep);
    
    // Move to next section
    if (currentStep < totalSteps) {
        currentStep++;
        updateUI();
    }
}

function previousSection() {
    if (currentStep > 1) {
        currentStep--;
        updateUI();
    }
}

function skipTrustedContact() {
    // Clear trusted contact fields
    document.getElementById('trustedName').value = '';
    document.getElementById('trustedEmail').value = '';
    document.getElementById('trustedPhone').value = '';
    document.getElementById('trustedRelationship').value = '';
    nextSection();
}

function updateUI() {
    // Hide all sections
    document.querySelectorAll('.form-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show current section
    const currentSection = document.getElementById(`section-${currentStep}`);
    if (currentSection) {
        currentSection.classList.add('active');
    }
    
    // Update progress bar
    document.querySelectorAll('.progress-step').forEach((step, index) => {
        const stepNumber = index + 1;
        if (stepNumber < currentStep) {
            step.classList.add('completed');
            step.classList.remove('active');
        } else if (stepNumber === currentStep) {
            step.classList.add('active');
            step.classList.remove('completed');
        } else {
            step.classList.remove('active', 'completed');
        }
    });
    
    // Update progress lines
    document.querySelectorAll('.progress-line').forEach((line, index) => {
        if (index < currentStep - 1) {
            line.classList.add('active');
        } else {
            line.classList.remove('active');
        }
    });
    
    // If on review section, populate review content
    if (currentStep === 7) {
        populateReview();
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function validateSection(step) {
    const errorElement = document.getElementById(`error-${step}`);
    if (errorElement) {
        errorElement.classList.remove('show');
        errorElement.textContent = '';
    }
    
    switch(step) {
        case 1:
            // Account type is pre-selected, always valid
            formData.accountType = 'stocks';
            break;
            
        case 2:
            const firstName = document.getElementById('firstName').value.trim();
            const lastName = document.getElementById('lastName').value.trim();
            const email = document.getElementById('email').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            if (!firstName || !lastName || !email || !phone || !password || !confirmPassword) {
                showError(step, 'Please fill in all required fields');
                return false;
            }
            
            if (!validateEmail(email)) {
                showError(step, 'Please enter a valid email address');
                return false;
            }
            
            if (password !== confirmPassword) {
                showError(step, 'Passwords do not match');
                return false;
            }
            
            if (password.length < 8) {
                showError(step, 'Password must be at least 8 characters long');
                return false;
            }
            
            if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password)) {
                showError(step, 'Password must contain uppercase, lowercase, and number');
                return false;
            }
            break;
            
        case 3:
            const dob = document.getElementById('dob').value;
            const ssn = document.getElementById('ssn').value.trim();
            
            if (!dob || !ssn) {
                showError(step, 'Please fill in all required fields');
                return false;
            }
            
            // Validate age (must be 18+)
            const birthDate = new Date(dob);
            const age = Math.floor((new Date() - birthDate) / (365.25 * 24 * 60 * 60 * 1000));
            if (age < 18) {
                showError(step, 'You must be at least 18 years old to open an account');
                return false;
            }
            break;
            
        case 4:
            const address1 = document.getElementById('address1').value.trim();
            const city = document.getElementById('city').value.trim();
            const state = document.getElementById('state').value;
            const zipCode = document.getElementById('zipCode').value.trim();
            
            if (!address1 || !city || !state || !zipCode) {
                showError(step, 'Please fill in all required fields');
                return false;
            }
            break;
            
        case 5:
            const employmentStatus = document.getElementById('employmentStatus').value;
            
            if (!employmentStatus) {
                showError(step, 'Please select your employment status');
                return false;
            }
            
            // Check if public company insider
            const isInsider = document.getElementById('insider-yes').checked;
            if (isInsider) {
                showError(step, 'Public company insiders cannot open an account');
                return false;
            }
            break;
            
        case 7:
            const agree1 = document.getElementById('agree1').checked;
            const agree2 = document.getElementById('agree2').checked;
            const agree3 = document.getElementById('agree3').checked;
            const agree4 = document.getElementById('agree4').checked;
            
            if (!agree1 || !agree2 || !agree3 || !agree4) {
                showError(step, 'Please agree to all terms and conditions');
                return false;
            }
            break;
    }
    
    return true;
}

function saveSectionData(step) {
    switch(step) {
        case 2:
            formData.profile.first_name = document.getElementById('firstName').value.trim();
            formData.profile.middle_name = document.getElementById('middleName').value.trim();
            formData.profile.last_name = document.getElementById('lastName').value.trim();
            formData.profile.preferred_name = document.getElementById('preferredName').value.trim();
            formData.email = document.getElementById('email').value.trim();
            formData.profile.phone = document.getElementById('phone').value.trim();
            formData.password = document.getElementById('password').value;
            
            // Military info
            formData.profile.has_military_experience = document.getElementById('military-yes').checked;
            if (formData.profile.has_military_experience) {
                formData.profile.military_status = document.getElementById('militaryStatus').value;
                formData.profile.military_branch = document.getElementById('militaryBranch').value;
                formData.profile.military_rank = document.getElementById('militaryRank').value;
            }
            break;
            
        case 3:
            formData.profile.date_of_birth = document.getElementById('dob').value;
            formData.profile.is_us_citizen = document.getElementById('citizen-yes').checked;
            formData.profile.ssn = document.getElementById('ssn').value.trim();
            break;
            
        case 4:
            formData.profile.address_line1 = document.getElementById('address1').value.trim();
            formData.profile.address_line2 = document.getElementById('address2').value.trim();
            formData.profile.city = document.getElementById('city').value.trim();
            formData.profile.state = document.getElementById('state').value;
            formData.profile.zip_code = document.getElementById('zipCode').value.trim();
            break;
            
        case 5:
            formData.profile.employment_status = document.getElementById('employmentStatus').value;
            formData.profile.job_title = document.getElementById('jobTitle').value.trim();
            formData.profile.employer_name = document.getElementById('employerName').value.trim();
            formData.profile.works_at_financial_institution = document.getElementById('fin-yes').checked;
            formData.profile.financial_institution_name = document.getElementById('financialInstitutionName').value.trim();
            formData.profile.is_public_company_insider = document.getElementById('insider-yes').checked;
            formData.profile.subject_to_backup_withholding = document.getElementById('backup-yes').checked;
            break;
            
        case 6:
            formData.profile.trusted_contact_name = document.getElementById('trustedName').value.trim();
            formData.profile.trusted_contact_email = document.getElementById('trustedEmail').value.trim();
            formData.profile.trusted_contact_phone = document.getElementById('trustedPhone').value.trim();
            formData.profile.trusted_contact_relationship = document.getElementById('trustedRelationship').value.trim();
            break;
    }
}

function populateReview() {
    const reviewContent = document.getElementById('review-content');
    
    const html = `
        <div class="review-section">
            <h3 class="review-header">Account Type</h3>
            <div class="review-item">
                <span class="review-label">Account Type:</span>
                <span class="review-value">Stocks & Funds</span>
            </div>
        </div>
        
        <div class="review-section">
            <h3 class="review-header">Personal Information</h3>
            <div class="review-item">
                <span class="review-label">Name:</span>
                <span class="review-value">${formData.profile.first_name} ${formData.profile.middle_name} ${formData.profile.last_name}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Email:</span>
                <span class="review-value">${formData.email}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Phone:</span>
                <span class="review-value">${formData.profile.phone}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Date of Birth:</span>
                <span class="review-value">${formData.profile.date_of_birth}</span>
            </div>
        </div>
        
        <div class="review-section">
            <h3 class="review-header">Address</h3>
            <div class="review-item">
                <span class="review-label">Address:</span>
                <span class="review-value">${formData.profile.address_line1}${formData.profile.address_line2 ? ', ' + formData.profile.address_line2 : ''}</span>
            </div>
            <div class="review-item">
                <span class="review-label">City, State ZIP:</span>
                <span class="review-value">${formData.profile.city}, ${formData.profile.state} ${formData.profile.zip_code}</span>
            </div>
        </div>
        
        <div class="review-section">
            <h3 class="review-header">Employment</h3>
            <div class="review-item">
                <span class="review-label">Status:</span>
                <span class="review-value">${formData.profile.employment_status}</span>
            </div>
            ${formData.profile.job_title ? `
            <div class="review-item">
                <span class="review-label">Job Title:</span>
                <span class="review-value">${formData.profile.job_title}</span>
            </div>
            ` : ''}
            ${formData.profile.employer_name ? `
            <div class="review-item">
                <span class="review-label">Employer:</span>
                <span class="review-value">${formData.profile.employer_name}</span>
            </div>
            ` : ''}
        </div>
        
        ${formData.profile.trusted_contact_name ? `
        <div class="review-section">
            <h3 class="review-header">Trusted Contact</h3>
            <div class="review-item">
                <span class="review-label">Name:</span>
                <span class="review-value">${formData.profile.trusted_contact_name}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Relationship:</span>
                <span class="review-value">${formData.profile.trusted_contact_relationship}</span>
            </div>
        </div>
        ` : ''}
    `;
    
    reviewContent.innerHTML = html;
}

async function submitForm() {
    if (!validateSection(7)) {
        return;
    }
    
    // Save final section data
    saveSectionData(7);
    
    // Show loading state
    const submitBtn = document.getElementById('submit-btn');
    const submitText = document.getElementById('submit-text');
    const submitLoading = document.getElementById('submit-loading');
    
    submitBtn.disabled = true;
    submitText.style.display = 'none';
    submitLoading.style.display = 'inline-block';
    
    try {
        // Submit to API
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: formData.email,
                password: formData.password,
                account_type: formData.accountType,
                profile_data: formData.profile
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Registration failed');
        }
        
        // Store token
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user_id', data.user_id);
        localStorage.setItem('user_email', data.email);
        
        // Show success message
        document.getElementById('section-7').classList.remove('active');
        document.getElementById('section-success').style.display = 'block';
        document.getElementById('section-success').classList.add('active');
        
        // Update progress to show completion
        document.querySelectorAll('.progress-step').forEach(step => {
            step.classList.add('completed');
            step.classList.remove('active');
        });
        document.querySelectorAll('.progress-line').forEach(line => {
            line.classList.add('active');
        });
        
    } catch (error) {
        console.error('Signup error:', error);
        showError(7, error.message || 'An error occurred during registration. Please try again.');
        
        // Reset button
        submitBtn.disabled = false;
        submitText.style.display = 'inline';
        submitLoading.style.display = 'none';
    }
}

function showError(step, message) {
    const errorElement = document.getElementById(`error-${step}`);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Toggle functions
function toggleMilitary(show) {
    const details = document.getElementById('military-details');
    if (details) {
        details.style.display = show ? 'block' : 'none';
    }
}

function toggleEmploymentFields() {
    const status = document.getElementById('employmentStatus').value;
    const details = document.getElementById('employment-details');
    if (details) {
        details.style.display = (status === 'employed' || status === 'self-employed') ? 'block' : 'none';
    }
}

function toggleFinancialInstitution() {
    const isYes = document.getElementById('fin-yes').checked;
    const nameField = document.getElementById('financial-institution-name');
    if (nameField) {
        nameField.style.display = isYes ? 'block' : 'none';
    }
}

function togglePublicCompany() {
    const isYes = document.getElementById('insider-yes').checked;
    const warning = document.getElementById('public-company-warning');
    if (warning) {
        warning.style.display = isYes ? 'block' : 'none';
    }
}

// Format SSN input
document.addEventListener('DOMContentLoaded', () => {
    const ssnInput = document.getElementById('ssn');
    if (ssnInput) {
        ssnInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 3 && value.length <= 5) {
                value = value.slice(0, 3) + '-' + value.slice(3);
            } else if (value.length > 5) {
                value = value.slice(0, 3) + '-' + value.slice(3, 5) + '-' + value.slice(5, 9);
            }
            e.target.value = value;
        });
    }
    
    // Format phone input
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 3 && value.length <= 6) {
                value = '(' + value.slice(0, 3) + ') ' + value.slice(3);
            } else if (value.length > 6) {
                value = '(' + value.slice(0, 3) + ') ' + value.slice(3, 6) + '-' + value.slice(6, 10);
            }
            e.target.value = value;
        });
    }
});
