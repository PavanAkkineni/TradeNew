# Logout Functionality - TradeCompass

## Overview

Complete logout functionality has been implemented with automatic session management and user menu integration.

## Features Implemented

### 1. **Logout Button in Navigation**
When users are logged in, the navigation automatically updates to show:
- User email
- Dropdown menu with:
  - Dashboard link
  - Settings link
  - **Logout button** (red, with icon)

### 2. **Automatic Token Verification**
- On every page load, the system verifies if the token is still valid
- If token is expired or invalid, user is automatically logged out
- Prevents users from accessing protected pages with expired tokens

### 3. **Session Management**
- Supports both `localStorage` (remember me) and `sessionStorage` (session only)
- Clears all authentication data on logout
- Calls backend logout API to invalidate session

### 4. **Protected Pages**
- Dashboard and other protected pages require authentication
- Automatically redirects to login if not authenticated
- Stores intended destination for redirect after login

### 5. **Login/Signup Redirect**
- If user is already logged in and tries to access login/signup pages
- Automatically redirects to dashboard or intended page

---

## Files Created/Modified

### New Files:
1. **`frontend/static/js/auth.js`** - Authentication utilities
   - `isLoggedIn()` - Check if user is authenticated
   - `logout()` - Logout user and clear session
   - `verifyToken()` - Verify token is still valid
   - `updateNavigation()` - Update nav based on auth status
   - `requireAuth()` - Protect pages requiring authentication
   - `redirectIfLoggedIn()` - Redirect if already logged in

2. **`frontend/dashboard.html`** - User dashboard (protected page)
   - Welcome banner
   - Quick access cards to features
   - Requires authentication to access

### Modified Files:
1. **`frontend/landing.html`** - Added auth.js script
2. **`frontend/login.html`** - Added auth.js and redirect check
3. **`frontend/signup.html`** - Added auth.js and redirect check
4. **`frontend/static/css/landing.css`** - Added user menu styles
5. **`frontend/static/js/login.js`** - Added redirect after login support

---

## How It Works

### User Flow - Logged In User

```
1. User logs in → Token stored in localStorage/sessionStorage
2. User navigates to any page → auth.js loads
3. auth.js checks if user is logged in
4. If logged in:
   - Updates navigation to show user menu
   - Verifies token is still valid
   - If invalid → Auto logout
5. User clicks dropdown → Shows Dashboard, Settings, Logout
6. User clicks Logout → Calls API, clears storage, redirects to /
```

### User Flow - Logged Out User

```
1. User visits protected page (e.g., /dashboard)
2. auth.js checks authentication
3. Not logged in → Stores intended page
4. Redirects to /login.html
5. User logs in → Redirects back to intended page
```

### User Flow - Already Logged In

```
1. Logged in user tries to access /login.html or /signup.html
2. auth.js detects user is already logged in
3. Automatically redirects to /dashboard
4. Prevents unnecessary login/signup
```

---

## User Menu UI

### When Logged In:
```
┌─────────────────────────────────┐
│ 👤 user@example.com ▼          │
└─────────────────────────────────┘
         ↓ (on click)
┌─────────────────────────────────┐
│ 📊 Dashboard                    │
│ ⚙️ Settings                     │
│ ─────────────────────────────   │
│ 🚪 Logout (red)                 │
└─────────────────────────────────┘
```

### When Logged Out:
```
┌─────────────────────────────────┐
│ [Sign In]  [Get Started]        │
└─────────────────────────────────┘
```

---

## API Integration

### Logout Endpoint
```javascript
POST /api/auth/logout
Headers: {
  Authorization: Bearer <token>
}
```

### Token Verification
```javascript
GET /api/auth/me
Headers: {
  Authorization: Bearer <token>
}
```

---

## Storage Management

### Data Stored:
- `access_token` - JWT authentication token
- `user_id` - User's ID
- `user_email` - User's email address
- `redirect_after_login` - Intended destination (sessionStorage only)

### Storage Locations:
- **localStorage** - When "Remember me" is checked (persistent)
- **sessionStorage** - When "Remember me" is NOT checked (session only)

### On Logout:
All authentication data is cleared from both storage locations.

---

## Security Features

### 1. Token Expiration
- Tokens expire after 7 days (configured in backend)
- Expired tokens are automatically detected
- User is logged out if token is invalid

### 2. Automatic Verification
- Token is verified on every page load
- Prevents access with expired/invalid tokens
- Graceful handling of verification failures

### 3. Session Cleanup
- All auth data cleared on logout
- Backend session invalidated
- No residual authentication data

### 4. Protected Routes
- Dashboard and other pages require valid authentication
- Automatic redirect to login if not authenticated
- Intended destination preserved for post-login redirect

---

## Usage Examples

### Protect a Page
```javascript
// At the top of your HTML file
<script src="static/js/auth.js"></script>
<script>
    if (!requireAuth()) {
        // User will be redirected to login
    }
</script>
```

### Check if Logged In
```javascript
if (isLoggedIn()) {
    // User is authenticated
    const user = getCurrentUser();
    console.log(user.email);
}
```

### Manual Logout
```javascript
// Call from anywhere
await logout();
// User will be logged out and redirected
```

### Get Current User
```javascript
const user = getCurrentUser();
if (user) {
    console.log(`Logged in as: ${user.email}`);
}
```

---

## Testing

### Test Logout Flow:
1. **Login** at `http://localhost:8000/login.html`
2. **Verify** navigation shows user menu with email
3. **Click** user menu → dropdown appears
4. **Click** "Logout" → redirected to landing page
5. **Verify** navigation shows "Sign In" and "Get Started" buttons
6. **Try** to access `/dashboard` → redirected to login

### Test Protected Pages:
1. **Logout** if logged in
2. **Navigate** to `http://localhost:8000/dashboard`
3. **Verify** redirected to login page
4. **Login** with credentials
5. **Verify** redirected back to dashboard

### Test Already Logged In:
1. **Login** at `http://localhost:8000/login.html`
2. **Navigate** to `/login.html` again
3. **Verify** automatically redirected to dashboard
4. **Navigate** to `/signup.html`
5. **Verify** automatically redirected to dashboard

### Test Token Expiration:
1. **Login** and get token
2. **Manually expire** token in backend (or wait 7 days)
3. **Refresh** any page
4. **Verify** automatically logged out

---

## Styling

### User Menu Styles:
- Dark theme matching landing page
- Smooth dropdown animation
- Hover effects on menu items
- Red logout button for emphasis
- Responsive design

### CSS Classes:
- `.user-menu` - Container for user menu
- `.user-menu-btn` - Button showing user email
- `.user-dropdown` - Dropdown menu
- `.dropdown-item` - Menu item
- `.logout-btn` - Logout button (red)

---

## Browser Compatibility

✅ Chrome/Edge (Chromium)
✅ Firefox
✅ Safari
✅ Mobile browsers

Uses standard Web APIs:
- `localStorage`
- `sessionStorage`
- `fetch` API
- DOM manipulation

---

## Future Enhancements

### Potential Improvements:
1. **Token Refresh** - Automatically refresh tokens before expiration
2. **Session Timeout** - Logout after X minutes of inactivity
3. **Multiple Device Management** - View and manage active sessions
4. **Logout All Devices** - Invalidate all sessions at once
5. **Activity Tracking** - Log all login/logout events
6. **2FA Integration** - Two-factor authentication support

---

## Troubleshooting

### User Not Logged Out on Refresh:
- Check if token is still valid
- Verify auth.js is loaded on the page
- Check browser console for errors

### Navigation Not Updating:
- Ensure auth.js is loaded before other scripts
- Check if `updateNavigation()` is called on DOMContentLoaded
- Verify CSS is properly loaded

### Redirect Loop:
- Check if requireAuth() is called on login/signup pages
- Verify redirectIfLoggedIn() is only on login/signup pages
- Check for conflicting redirect logic

### Token Not Cleared:
- Verify logout() function is called
- Check both localStorage and sessionStorage
- Clear browser cache if needed

---

## Summary

✅ **Complete logout functionality** with API integration
✅ **User menu dropdown** with logout button
✅ **Automatic token verification** on page load
✅ **Protected pages** with authentication requirement
✅ **Session management** with localStorage/sessionStorage
✅ **Redirect handling** for better UX
✅ **Security features** with token expiration
✅ **Responsive design** matching app theme

The logout system is **production-ready** and provides a seamless authentication experience! 🎉
