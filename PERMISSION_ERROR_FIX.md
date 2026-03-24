# Permission Error Fix - Complete Solution

## Problem
You were getting: **"You do not have permission to upload students"** (403 Forbidden error)

## Root Cause
The REST Framework authentication wasn't recognizing the custom JWT token format created by the login endpoint.

## Solution Applied ✅

I've implemented a **Custom JWT Authentication Class** that:
- ✅ Properly decodes your login endpoint's JWT tokens
- ✅ Authenticates users with those tokens
- ✅ Allows authenticated users to upload CSV files
- ✅ Provides clear error messages if authentication fails

## Changes Made

1. **Added CustomJWTAuthentication class** - Handles your custom JWT token format
2. **Updated authentication stack** - Now supports:
   - Custom JWT tokens (from login endpoint)
   - Session authentication (browser cookies)
   - Django REST Framework JWT (backup)
3. **Improved StudentViewSet** - Now uses the custom authentication
4. **Updated settings.py** - Registered new authentication class

## What You Need To Do NOW

### Step 1: Restart Django Server

**Important:** You MUST restart the server for the changes to take effect.

Stop the current server:
```bash
# Press Ctrl+C in the terminal running Django
```

Start again:
```bash
python manage.py runserver
```

### Step 2: Clear Browser Cache & Cookies

To clear all authentication data:
1. Press **Ctrl + Shift + Delete** (Windows/Linux)
   - Or **Cmd + Shift + Delete** (Mac)
2. Select "All time"
3. Check "Cookies and other site data"
4. Click **Clear data**

Or use **Incognito/Private mode** for a clean test.

### Step 3: Test Again

Now try:
1. Go to http://localhost:8000/
2. Login with admin/admin123
3. Go to Admin Dashboard
4. Click "Upload CSV" button
5. Upload should now work! ✅

## If Still Getting "You do not have permission"

### Check These Things:

**1. Check browser console for actual error:**
- Press F12
- Go to Console tab
- Look for error messages
- Check Network tab → POST to `students/bulk_upload/`

**2. Verify admins are set up:**
```bash
python manage.py shell
```
Then run:
```python
from django.contrib.auth.models import User
from home.models import AdminUser

# Check if admin user exists
user = User.objects.filter(username='admin').first()
print("Admin user:", user)

# Check if admin role exists
admin_role = AdminUser.objects.filter(user=user).first()
print("Admin role:", admin_role)
print("Admin role type:", admin_role.role if admin_role else "NOT FOUND")
```

**3. Ensure demo data is set up:**
```bash
python setup_demo_data.py
```

This creates the admin user and role properly.

## For CSV Upload to Work

You need:
1. ✅ Django server running
2. ✅ User logged in as admin
3. ✅ Valid JWT token in browser's localStorage
4. ✅ CSV file prepared
5. ✅ Custom authentication class installed (done - just restart server)

## Test the API Directly

You can test the endpoint with curl:

```bash
# 1. Get token from login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username":"admin",
    "password":"admin123",
    "role":"admin"
  }'

# This returns token. Copy it.
# Then use it for CSV upload:

curl -X POST http://localhost:8000/api/students/bulk_upload/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "csv_file=@sample_students.csv"
```

## How Authentication Now Works

```
1. User logs in at http://localhost:8000/
   ↓
2. Backend returns custom JWT token with secret 'hall_ticket_secret'
   ↓
3. Frontend stores token in localStorage
   ↓
4. Frontend sends token in "Authorization: Bearer TOKEN" header
   ↓
5. CustomJWTAuthentication class validates token
   ↓
6. If valid → User is authenticated → Can upload CSV ✅
   If invalid → Error → Ask to login again
```

## Common Issues After Restart

| Issue | Solution |
|-------|----------|
| Still getting 403 | Restart server + clear cache |
| Token invalid error | Login again to get new token |
| Cannot find module | Restart server (Python needs to reload) |
| Still not working | Run `python setup_demo_data.py` to ensure admin exists |

## Files Changed

- `home/views.py` - Added CustomJWTAuthentication class
- `HALLTICKETT/settings.py` - Updated REST_FRAMEWORK authentication classes  

## Next Steps

After fixing this:
1. ✅ Upload CSV with student data
2. ✅ Create exams
3. ✅ Generate hall tickets
4. ✅ Use QR code scanner

All features should work now!
