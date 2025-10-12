// Login Form JavaScript

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    const loginText = document.getElementById('loginText');
    const loginLoading = document.getElementById('loginLoading');
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');
    
    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
        // Verify token is still valid
        verifyToken(token).then(valid => {
            if (valid) {
                window.location.href = '/dashboard';
            }
        });
    }
    
    // Handle form submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Clear previous messages
        hideError();
        hideSuccess();
        
        // Get form data
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const remember = document.getElementById('remember').checked;
        
        // Validate
        if (!email || !password) {
            showError('Please enter both email and password');
            return;
        }
        
        if (!validateEmail(email)) {
            showError('Please enter a valid email address');
            return;
        }
        
        // Show loading state
        loginBtn.disabled = true;
        loginText.style.display = 'none';
        loginLoading.style.display = 'inline-block';
        
        try {
            // Call login API
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Login failed');
            }
            
            // Store token and user info
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_email', data.email);
            
            // If remember me is checked, store in localStorage (already done)
            // Otherwise, we could use sessionStorage
            if (!remember) {
                // Move to sessionStorage instead
                sessionStorage.setItem('access_token', data.access_token);
                sessionStorage.setItem('user_id', data.user_id);
                sessionStorage.setItem('user_email', data.email);
                localStorage.removeItem('access_token');
                localStorage.removeItem('user_id');
                localStorage.removeItem('user_email');
            }
            
            // Show success message
            showSuccess('Login successful! Redirecting...');
            
            // Redirect to intended page or dashboard after short delay
            setTimeout(() => {
                const redirect = sessionStorage.getItem('redirect_after_login') || '/dashboard';
                sessionStorage.removeItem('redirect_after_login');
                window.location.href = redirect;
            }, 1000);
            
        } catch (error) {
            console.error('Login error:', error);
            showError(error.message || 'Invalid email or password. Please try again.');
            
            // Reset button
            loginBtn.disabled = false;
            loginText.style.display = 'inline';
            loginLoading.style.display = 'none';
        }
    });
    
    // Handle Enter key in password field
    document.getElementById('password').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            loginForm.dispatchEvent(new Event('submit'));
        }
    });
});

async function verifyToken(token) {
    try {
        const response = await fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        return response.ok;
    } catch (error) {
        return false;
    }
}

function showError(message) {
    const errorElement = document.getElementById('error-message');
    errorElement.textContent = message;
    errorElement.classList.add('show');
}

function hideError() {
    const errorElement = document.getElementById('error-message');
    errorElement.classList.remove('show');
    errorElement.textContent = '';
}

function showSuccess(message) {
    const successElement = document.getElementById('success-message');
    successElement.textContent = message;
    successElement.classList.add('show');
}

function hideSuccess() {
    const successElement = document.getElementById('success-message');
    successElement.classList.remove('show');
    successElement.textContent = '';
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Handle forgot password (placeholder)
document.addEventListener('DOMContentLoaded', () => {
    const forgotLink = document.querySelector('.forgot-link');
    if (forgotLink) {
        forgotLink.addEventListener('click', (e) => {
            e.preventDefault();
            alert('Password reset functionality coming soon! Please contact support for assistance.');
        });
    }
});
