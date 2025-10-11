# Quick Start Guide - TradeCompass Authentication

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd /Users/ruthvikakosuri/Desktop/TradeCompass
pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
python init_db.py
```

### Step 3: Start Server
```bash
python run_app.py
```

Then open your browser to: **http://localhost:8000**

---

## 📋 What You'll See

### Landing Page (`http://localhost:8000`)
- Beautiful dark-themed landing page
- Two account options: Stocks & Funds or Stocks, Funds & Crypto
- Click **"Get Started"** to create an account

### Signup Flow (`http://localhost:8000/signup.html`)
Complete 7 easy steps:
1. ✅ Choose account type
2. ✅ Enter basic info (name, email, phone, password)
3. ✅ Security info (DOB, SSN, citizenship)
4. ✅ Address
5. ✅ Employment details
6. ✅ Trusted contact (optional)
7. ✅ Review and confirm

### Login Page (`http://localhost:8000/login.html`)
- Sign in with email and password
- Remember me option
- Automatic redirect to dashboard

---

## 🧪 Test Account Creation

### Quick Test
1. Go to `http://localhost:8000`
2. Click "Get Started"
3. Fill out the form with test data:
   - **Email**: test@example.com
   - **Password**: Test1234
   - **Account Type**: Stocks, Funds & Crypto
   - Fill in other required fields
4. Submit and verify success!

### Test Login
1. Go to `http://localhost:8000/login.html`
2. Enter your test credentials
3. Click "Sign In"
4. You'll be redirected to `/dashboard`

---

## 🔐 Security Features

✅ **Password Hashing**: Bcrypt with salt
✅ **SSN Encryption**: Fernet symmetric encryption
✅ **JWT Tokens**: 7-day expiration
✅ **Session Tracking**: IP and user agent logging
✅ **Activity Logs**: All user actions recorded
✅ **Input Validation**: Email, password strength, age verification

---

## 📁 Key Files

### Backend
- `app/database.py` - Database models
- `app/auth.py` - Authentication logic
- `app/main.py` - API endpoints (lines 562-735)

### Frontend
- `frontend/landing.html` - Landing page
- `frontend/signup.html` - Signup form
- `frontend/login.html` - Login page

### Database
- `tradecompass.db` - SQLite database (created after init_db.py)

---

## 🎯 User Flow

```
Landing Page (/)
    ↓
    [Get Started] → Signup (/signup.html)
    ↓
    7-Step Form
    ↓
    Account Created ✅
    ↓
    Auto Login
    ↓
    Dashboard (/dashboard)

OR

Landing Page (/)
    ↓
    [Sign In] → Login (/login.html)
    ↓
    Enter Credentials
    ↓
    Dashboard (/dashboard)
```

---

## 💡 Tips

- **Passwords must have**: 8+ chars, uppercase, lowercase, number
- **Age requirement**: Must be 18 or older
- **Public company insiders**: Cannot create accounts
- **Trusted contact**: Optional but recommended
- **Remember me**: Stores token in localStorage vs sessionStorage

---

## 🐛 Troubleshooting

**Database not found?**
```bash
python init_db.py
```

**Port 8000 in use?**
```bash
lsof -ti:8000 | xargs kill -9
python run_app.py
```

**Import errors?**
```bash
pip install -r requirements.txt --force-reinstall
```

**Can't login?**
- Check browser console for errors
- Verify email/password are correct
- Clear localStorage: `localStorage.clear()`

---

## 📊 Database Tables Created

1. **users** - User accounts (email, password, account_type)
2. **user_profiles** - Detailed user info (name, address, employment, etc.)
3. **user_sessions** - Active sessions with tokens
4. **user_activities** - Activity logs (signup, login, etc.)

---

## 🎨 Features Implemented

### Landing Page
✅ Animated gradient background
✅ Account type cards with hover effects
✅ Feature highlights
✅ Security badges
✅ Smooth scrolling
✅ Responsive design

### Signup Page
✅ Multi-step progress indicator
✅ Real-time validation
✅ Password strength checker
✅ SSN formatting (XXX-XX-XXXX)
✅ Phone formatting ((555) 123-4567)
✅ Military service section
✅ Employment verification
✅ Review before submit
✅ Success animation

### Login Page
✅ Clean, modern design
✅ Remember me checkbox
✅ Forgot password link
✅ Social login placeholders
✅ Error handling
✅ Loading states

---

## 🔗 API Endpoints

- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Sign in
- `POST /api/auth/logout` - Sign out
- `GET /api/auth/me` - Get user info
- `GET /api/auth/check-email/{email}` - Check email availability

---

## ✅ Ready to Use!

Your authentication system is fully functional and ready for testing. All user data is securely stored with encryption and proper validation.

**Next Steps:**
1. Test the signup flow
2. Test the login flow
3. Verify data is saved in database
4. Customize styling if needed
5. Add email verification (optional)
6. Deploy to production

For detailed documentation, see `AUTHENTICATION_SETUP.md`
