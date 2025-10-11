// Landing Page JavaScript

// Add scroll effect to navbar
window.addEventListener('scroll', function() {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            entry.target.classList.add('animated');
        }
    });
}, observerOptions);

// Observe feature cards and account cards
document.querySelectorAll('.feature-card, .account-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'all 0.6s ease';
    observer.observe(el);
});

// Animated counter for stats
function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            element.textContent = formatNumber(end);
            clearInterval(timer);
        } else {
            element.textContent = formatNumber(Math.floor(current));
        }
    }, 16);
}

function formatNumber(num) {
    if (num >= 1000) {
        return '$' + (num / 1000).toFixed(0) + 'k';
    }
    return '$' + num.toLocaleString();
}

// Simulate live data updates
function updateDashboardStats() {
    const portfolioValue = document.querySelector('.stat-value');
    if (portfolioValue && portfolioValue.textContent === '$125,430') {
        // Add slight variations to make it look live
        const baseValue = 125430;
        const variation = Math.floor(Math.random() * 1000) - 500;
        const newValue = baseValue + variation;
        portfolioValue.textContent = '$' + newValue.toLocaleString();
        
        // Update change percentage
        const changePercent = ((variation / baseValue) * 100).toFixed(2);
        const changeElement = portfolioValue.parentElement.querySelector('.stat-change');
        if (changeElement) {
            changeElement.textContent = (variation >= 0 ? '+' : '') + changePercent + '%';
            changeElement.style.color = variation >= 0 ? 'var(--secondary-color)' : 'var(--danger-color)';
        }
    }
}

// Update stats every 3 seconds
setInterval(updateDashboardStats, 3000);

// Handle account type selection
document.querySelectorAll('.account-card .btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        const url = new URL(this.href, window.location.origin);
        const accountType = url.searchParams.get('type');
        if (accountType) {
            // Store the selected account type for the signup page
            localStorage.setItem('selectedAccountType', accountType);
        }
    });
});

// Add hover effect to feature cards
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        const icon = this.querySelector('.feature-icon');
        if (icon) {
            icon.style.transform = 'scale(1.1) rotate(5deg)';
        }
    });
    
    card.addEventListener('mouseleave', function() {
        const icon = this.querySelector('.feature-icon');
        if (icon) {
            icon.style.transform = 'scale(1) rotate(0deg)';
        }
    });
});

// Add transition to feature icons
document.querySelectorAll('.feature-icon').forEach(icon => {
    icon.style.transition = 'transform 0.3s ease';
});

// Parallax effect for floating elements
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const parallax = document.querySelectorAll('.floating-element');
    
    parallax.forEach(element => {
        const speed = element.classList.contains('floating-1') ? 0.5 : 
                      element.classList.contains('floating-2') ? 0.3 : 0.4;
        const yPos = -(scrolled * speed);
        element.style.transform = `translateY(${yPos}px)`;
    });
});

// Add loading animation to dashboard
const loadingSpinner = document.querySelector('.loading-spinner');
if (loadingSpinner) {
    setTimeout(() => {
        loadingSpinner.style.display = 'none';
        // Show success indicator
        const header = document.querySelector('.dashboard-header');
        if (header) {
            const liveIndicator = document.createElement('span');
            liveIndicator.innerHTML = '🟢 Live';
            liveIndicator.style.color = 'var(--secondary-color)';
            liveIndicator.style.fontSize = '0.9rem';
            liveIndicator.style.animation = 'pulse 2s infinite';
            header.appendChild(liveIndicator);
        }
    }, 2000);
}

// Mobile menu toggle (if needed in future)
function createMobileMenu() {
    const navbar = document.querySelector('.navbar');
    const mobileMenuBtn = document.createElement('button');
    mobileMenuBtn.className = 'mobile-menu-btn';
    mobileMenuBtn.innerHTML = '☰';
    mobileMenuBtn.style.display = 'none';
    
    // Only show on mobile
    if (window.innerWidth <= 768) {
        mobileMenuBtn.style.display = 'block';
    }
    
    window.addEventListener('resize', () => {
        if (window.innerWidth <= 768) {
            mobileMenuBtn.style.display = 'block';
        } else {
            mobileMenuBtn.style.display = 'none';
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    createMobileMenu();
    
    // Add fade-in animation to hero content
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
        heroContent.style.opacity = '0';
        setTimeout(() => {
            heroContent.style.opacity = '1';
            heroContent.style.transition = 'opacity 1s ease';
        }, 100);
    }
    
    // Log page view (for analytics if needed)
    console.log('TradeCompass Landing Page Loaded');
});
