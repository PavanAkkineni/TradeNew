// Header component for all pages
// This ensures consistent navigation with logout button across the entire app

/**
 * Initialize header on page load
 */
function initializeHeader() {
    // Check if header already has nav-links
    const existingNavLinks = document.querySelector('.nav-links');
    if (existingNavLinks) {
        // Update existing navigation
        updateNavigation();
    } else {
        // Create header if it doesn't exist
        createHeader();
    }
}

/**
 * Create header for pages that don't have one
 */
function createHeader() {
    // Check if header already exists
    if (document.querySelector('.header')) {
        return;
    }
    
    const header = document.createElement('header');
    header.className = 'header';
    header.innerHTML = `
        <div class="header-container">
            <a href="/" class="logo">
                <span>📈</span>
                TradeCompass
            </a>
            <div class="nav-links">
                <!-- Will be populated by auth.js -->
            </div>
        </div>
    `;
    
    // Insert at the beginning of body
    document.body.insertBefore(header, document.body.firstChild);
    
    // Update navigation based on auth status
    updateNavigation();
}

/**
 * Add logout button to any page
 * Call this function on pages that need a quick logout button
 */
function addLogoutButton(containerId = 'logout-container') {
    const container = document.getElementById(containerId);
    if (!container) {
        console.warn(`Container #${containerId} not found for logout button`);
        return;
    }
    
    if (isLoggedIn()) {
        const user = getCurrentUser();
        container.innerHTML = `
            <div class="quick-logout">
                <span class="user-info">👤 ${user.email}</span>
                <button onclick="logout()" class="btn-logout">
                    <span>🚪</span> Logout
                </button>
            </div>
        `;
    }
}

// Initialize header when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeHeader();
});
