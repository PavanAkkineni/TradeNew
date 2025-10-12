// Authentication utilities for TradeCompass

/**
 * Check if user is logged in
 */
function isLoggedIn() {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    return !!token;
}

/**
 * Get current user's access token
 */
function getAccessToken() {
    return localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
}

/**
 * Get current user info from storage
 */
function getCurrentUser() {
    const userId = localStorage.getItem('user_id') || sessionStorage.getItem('user_id');
    const email = localStorage.getItem('user_email') || sessionStorage.getItem('user_email');
    
    if (!userId || !email) return null;
    
    return {
        id: userId,
        email: email
    };
}

/**
 * Logout user
 */
async function logout() {
    const token = getAccessToken();
    
    if (token) {
        try {
            // Call logout API
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        } catch (error) {
            console.error('Logout API error:', error);
        }
    }
    
    // Clear all auth data from storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('user_id');
    sessionStorage.removeItem('user_email');
    
    // Redirect to landing page
    window.location.href = '/';
}

/**
 * Verify token is still valid
 */
async function verifyToken() {
    const token = getAccessToken();
    if (!token) return false;
    
    try {
        const response = await fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        return response.ok;
    } catch (error) {
        console.error('Token verification error:', error);
        return false;
    }
}

/**
 * Update navigation based on auth status
 */
async function updateNavigation() {
    const navLinks = document.querySelector('.nav-links');
    if (!navLinks) return;
    
    if (isLoggedIn()) {
        // Verify token is still valid
        const isValid = await verifyToken();
        
        if (!isValid) {
            // Token expired, logout
            await logout();
            return;
        }
        
        const user = getCurrentUser();
        
        // Replace Sign In and Get Started buttons with user menu
        navLinks.innerHTML = `
            <a href="/dashboard" class="nav-link">Dashboard</a>
            <div class="user-menu">
                <button class="user-menu-btn" onclick="toggleUserMenu()">
                    <span class="user-icon">👤</span>
                    <span class="user-email">${user.email}</span>
                    <span class="dropdown-arrow">▼</span>
                </button>
                <div class="user-dropdown" id="userDropdown" style="display: none;">
                    <a href="/dashboard" class="dropdown-item">
                        <span>📊</span> Dashboard
                    </a>
                    <a href="/profile" class="dropdown-item">
                        <span>⚙️</span> Settings
                    </a>
                    <div class="dropdown-divider"></div>
                    <button onclick="logout()" class="dropdown-item logout-btn">
                        <span>🚪</span> Logout
                    </button>
                </div>
            </div>
        `;
    } else {
        // Show default Sign In and Get Started buttons
        navLinks.innerHTML = `
            <a href="/login.html" class="btn btn-secondary">Sign In</a>
            <a href="/signup.html" class="btn btn-primary">Get Started</a>
        `;
    }
}

/**
 * Toggle user dropdown menu
 */
function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    }
}

/**
 * Close dropdown when clicking outside
 */
document.addEventListener('click', function(event) {
    const userMenu = document.querySelector('.user-menu');
    const dropdown = document.getElementById('userDropdown');
    
    if (userMenu && dropdown && !userMenu.contains(event.target)) {
        dropdown.style.display = 'none';
    }
});

/**
 * Initialize auth on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    updateNavigation();
});

/**
 * Require authentication for protected pages
 */
function requireAuth() {
    if (!isLoggedIn()) {
        // Store the intended destination
        sessionStorage.setItem('redirect_after_login', window.location.pathname);
        window.location.href = '/login.html';
        return false;
    }
    return true;
}

/**
 * Redirect if already logged in (for login/signup pages)
 */
function redirectIfLoggedIn() {
    if (isLoggedIn()) {
        const redirect = sessionStorage.getItem('redirect_after_login') || '/dashboard';
        sessionStorage.removeItem('redirect_after_login');
        window.location.href = redirect;
    }
}
