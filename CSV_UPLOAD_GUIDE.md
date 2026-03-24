# CSV Upload Troubleshooting Guide

## Quick Test Steps

1. **Start the server** (from the HALLTICKETT directory):
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

2. **Apply the email field migration** (if needed):
   ```bash
   python manage.py migrate home
   ```

3. **Login to admin dashboard**
   - Go to: http://localhost:8000/
   - Admin login: admin / admin123
   - Or Staff login: staff / staff123

4. **Test CSV Upload**
   - Click "Upload CSV" button
   - Select [sample_students.csv](./sample_students.csv)
   - Click Upload

## CSV Format Requirements

Your CSV file must have these columns (in any order):
- `roll_number` (Required) - Student roll number (e.g., CS001)
- `name` (Required) - Student full name
- `email` (Required) - Valid email address
- `phone` (Optional) - Phone number
- `gender` (Optional) - M, F, or O
- `batch` (Optional) - Batch year (e.g., 2024)
- `branch` (Optional) - Branch name (e.g., Computer Science)

### Example CSV:
```
roll_number,name,email,phone,gender,batch,branch
CS001,John Doe,john@example.com,9876543210,M,2024,Computer Science
CS002,Jane Smith,jane@example.com,9876543211,F,2024,Computer Science
EC001,Bob Johnson,bob@example.com,9876543212,M,2024,Electronics
```

## Common Issues & Solutions

### Issue: "Error uploading CSV - undefined"
**Solution:**
- Check browser console (F12) for detailed error messages
- Verify you're logged in (token might have expired)
- Make sure CSV file has all required columns

### Issue: "Connection error"
**Solution:**
- Verify Django server is running
- Check that API_URL in page matches your server URL
- Check network tab in browser developer tools

### Issue: "You are not authenticated"
**Solution:**
- Log out and log back in
- Clear browser cache/localStorage
- Check console to verify token is being saved

### Issue: "CSV file is missing required columns"
**Solution:**
- Ensure your CSV has headers: `roll_number`, `name`, `email`
- Check spelling is exact (case-sensitive in some cases)
- Re-download the sample file if needed

### Issue: Some rows fail but others succeed
**Solution:**
- Check the warning notification for specific row errors
- Review the sample CSV for correct formatting
- Ensure no duplicate emails or roll numbers in the same upload

## Database Migration Status

The Student model email field has been updated to allow non-unique emails (to support updates).
Run migrations:
```bash
python manage.py migrate home
```

## Debug Information

To check API status:
```
GET http://localhost:8000/api/status/
```

This will show:
- Database connection status
- Student count
- Exam count

## Debugging Steps

1. **Open browser console** (F12 key)
2. **Go to Admin Dashboard**
3. **Click Upload CSV**
4. **Watch console** for detailed logs
5. **Check "Network" tab** to see API request/response
6. **Look for error messages** in the notification

## Sample CSV Provided

A sample CSV file is included: [sample_students.csv](./sample_students.csv)

You can:
- Use it as-is for testing
- Modify it with your own data
- Use it as a template for bulk imports
