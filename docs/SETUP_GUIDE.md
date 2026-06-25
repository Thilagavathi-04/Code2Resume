# 🚀 Quick Start Guide - Code2Resume

## Database & Authentication Setup

### ✅ Current Status

The application is now fully configured with:
- ✓ SQLite database with updated schema
- ✓ User authentication (register/login)
- ✓ JWT token-based sessions
- ✓ All user fields properly stored

### 📦 Database Schema

**Users Table:**
```
- id (Primary Key)
- username (Unique, Required)
- hashed_password (Bcrypt, Required)
- github_url (Required)
- github_token (Required, Hidden in UI)
- gmail (Required)
- mobile_number (Required)
- linkedin_id (Optional)
- leetcode_id (Optional)
```

## 🎯 Starting the Application

### Method 1: Using the new start script (Recommended)
```bash
./start.sh
```

This will:
1. Check for virtual environment
2. Verify database exists
3. Test database schema
4. Start the server

### Method 2: Using the original run script
```bash
./run.sh
```

### Method 3: Manual start
```bash
source env/bin/activate
cd backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

## 🌐 Available Pages

Once the server is running, access:

- **Login:** http://localhost:8001/
- **Register:** http://localhost:8001/register
- **Dashboard:** http://localhost:8001/dashboard (requires auth)
- **Settings:** http://localhost:8001/settings (requires auth)
- **Test Suite:** http://localhost:8001/test-auth (for testing)

## 🧪 Testing the Setup

1. **Test Database:**
   ```bash
   ./env/bin/python test_db.py
   ```

2. **Test Registration & Login:**
   - Go to http://localhost:8001/test-auth
   - Follow the test steps to verify everything works

## 🔧 Database Management

### Reset Database (if schema changes)
```bash
./env/bin/python init_db.py
```

### Manual Database Check
```bash
# View database schema
echo "PRAGMA table_info(users);" | sqlite3 users.db

# Count users
echo "SELECT COUNT(*) FROM users;" | sqlite3 users.db

# View all users (be careful in production!)
echo "SELECT username, gmail FROM users;" | sqlite3 users.db
```

## 📝 Registration Flow

1. User visits `/register`
2. Fills in required fields:
   - Username
   - Password
   - Gmail
   - Mobile Number
   - GitHub URL
   - GitHub Personal Access Token
   - LinkedIn ID (optional)
   - LeetCode ID (optional)
3. Frontend validates GitHub token with GitHub API
4. User data is stored in SQLite database
5. JWT token is generated and returned
6. User is redirected to `/dashboard`

## 🔐 Login Flow

1. User visits `/` (login page)
2. Enters username and password
3. Backend verifies credentials with bcrypt
4. JWT token is generated (expires in 30 minutes)
5. Token stored in localStorage
6. User redirected to `/dashboard`

## ⚙️ Settings Page

Users can update:
- ✏️ Password
- ✏️ Gmail
- ✏️ Mobile Number
- ✏️ GitHub URL
- ✏️ LinkedIn ID
- ✏️ LeetCode ID

**Cannot be changed:**
- 🔒 Username
- 🔒 GitHub Token

## 🚨 Troubleshooting

### "no such column: users.linkedin_id"
**Solution:** Database schema is outdated
```bash
rm users.db
./env/bin/python init_db.py
```

### "ModuleNotFoundError: No module named 'sqlalchemy'"
**Solution:** Use virtual environment Python
```bash
source env/bin/activate
./env/bin/python init_db.py
```

### Cannot login after registration
**Solution:** 
1. Check browser console for errors
2. Verify token is being stored in localStorage
3. Check backend logs for authentication errors

### GitHub token validation fails
**Solution:**
- Generate a new GitHub Personal Access Token
- Go to: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- Generate new token with 'repo' scope
- Use the token starting with `ghp_`

## 📊 Database Files

- **users.db** - Main database (SQLite)
- Created automatically on first run
- Location: Project root directory

## 🔒 Security Notes

1. **Passwords:** Hashed with bcrypt (never stored in plaintext)
2. **JWT Tokens:** Expire after 30 minutes
3. **GitHub Tokens:** Stored securely, not editable in UI
4. **CORS:** Enabled for all origins (disable in production)

## 🎨 UI Design

All pages now feature:
- Modern gradient design (purple theme)
- Responsive layout
- Clean form validation
- Success/error messages
- Smooth animations

## 📱 Mobile Support

All pages are fully responsive and work on:
- Desktop browsers
- Tablets
- Mobile phones

## 🔄 Next Steps

After successful login:
1. Go to dashboard
2. Click "Update from GitHub" to analyze repositories
3. Use chat to generate resumes
4. Visit settings to update profile information

---

**Need help?** Check the test page at http://localhost:8001/test-auth
