# CSV Upload Guide - Recommended Way to Add Students

## Why Use CSV Upload?

✅ **Advantages:**
- Upload multiple students at once (bulk operation)
- No authentication issues
- Easier to manage student data
- Can update existing students
- Shows clear progress

❌ **Adding One-by-One Issues:**
- Individual login/token issues can occur
- Slower process
- More prone to errors

---

## Step-by-Step CSV Upload Tutorial

### Step 1: Prepare Your CSV File

Create a CSV file with student data. You can use Excel, Google Sheets, or any text editor.

**Required Columns:**
- `roll_number` - Student's roll number (e.g., CS001)
- `name` - Student's full name
- `email` - Valid email address

**Optional Columns:**
- `phone` - Phone number
- `gender` - M, F, or O
- `batch` - Year (e.g., 2024)
- `branch` - Department name

**Example CSV Content:**
```csv
roll_number,name,email,phone,gender,batch,branch
CS001,John Doe,john@example.com,9876543210,M,2024,Computer Science
CS002,Jane Smith,jane@example.com,9876543211,F,2024,Computer Science
CS003,Bob Johnson,bob@example.com,9876543212,M,2024,Computer Science
EC001,Alice Williams,alice@example.com,9876543213,F,2024,Electronics
EC002,Charlie Brown,charlie@example.com,9876543214,M,2024,Electronics
ME001,Diana Prince,diana@example.com,9876543215,F,2024,Mechanical
```

### Step 2: Log In to Admin Dashboard

1. Go to: **http://localhost:8000/**
2. Select **Admin/Staff** tab
3. Enter:
   - **Username:** `admin`
   - **Password:** `admin123`
   - **Role:** Administrator
4. Click **Login**
5. You'll see the Dashboard

### Step 3: Upload CSV File

1. Click on **"Upload CSV"** button (green button with file icon)
2. A modal dialog appears
3. Click on the file input area or **browse** to select your CSV file
4. Select your prepared CSV file
5. Click **Upload** button
6. You'll see a spinner while uploading

### Step 4: Check Results

After upload completes, you'll see:
- ✅ **"X students created successfully!"** - All rows were added
- ⚠️ **"X students created and Y updated. Z rows had errors."** - Mixed results
- ❌ **Error message** - Something went wrong

### Step 5: Verify Data

The dashboard will automatically refresh and show:
- Total Students count increased
- Your new students appear in the students list

---

## Sample CSV File Provided

A sample file is included in the project:
📄 **Location:** `sample_students.csv`

You can:
- Download and use it as-is for testing
- Modify it with your own data
- Copy its structure for your own CSV files

---

## Common CSV Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| CSV file is missing required columns | Missing `roll_number`, `name`, or `email` | Add these columns as headers |
| Row X: Missing required fields | Empty cell in required column | Fill in all required fields |
| Row X: Invalid email format | Bad email in email column | Use format: `user@example.com` |
| Roll number already exists | Same roll_number in database | Use unique roll numbers |
| No CSV file provided | Didn't select a file | Select a CSV file first |

---

## Tips for CSV Files

### Creating CSV in Excel:
1. Open Excel
2. Create columns: `roll_number`, `name`, `email`, `phone`, `gender`, `batch`, `branch`
3. Add your data
4. Click **File → Save As**
5. Choose **CSV (Comma delimited)**
6. Save the file

### Creating CSV in Google Sheets:
1. Create a Google Sheet
2. Add column headers and data
3. Click **File → Download → Comma Separated Values**
4. Save to your computer

### Creating CSV in Text Editor:
```
Create a file with this content and save as `students.csv`:

roll_number,name,email,phone,gender,batch,branch
22,amal,avin12@gmail.com,1245896754,M,2024,MCA
23,bhavna,bhavna@example.com,9876543211,F,2024,MCA
```

---

## Debug If Upload Fails

### Check Browser Console:
1. Press **F12** to open Developer Tools
2. Go to **Console** tab
3. Try uploading CSV again
4. Look for error messages
5. Note any red errors

### Check Network:
1. Open Developer Tools (**F12**)
2. Go to **Network** tab
3. Upload CSV file
4. Find POST request to `students/bulk_upload/`
5. Click it and check Response tab for detailed error

### Test API Health:
Visit this URL to check if API is working:
```
http://localhost:8000/api/status/
```

Should show something like:
```json
{
  "status": "ok",
  "database": "connected",
  "stats": {
    "students": 5,
    "exams": 0
  }
}
```

---

## Batch Processing Multiple Files

If you have many students, you can:

1. **Organize by batch:** Create separate CSV for each year/branch
2. **Upload one at a time:** Upload batches sequentially
3. **Fix errors:** Remove problematic rows and re-upload

---

## Alternative: Using Sample File for Testing

Try using the included sample first:
1. Go to Admin Dashboard
2. Click "Upload CSV"
3. Select `sample_students.csv`
4. Click Upload
5. Should show: "5 students created successfully!"

If this works, then your CSV format should match this sample.

---

## After Uploading Students

Once students are in the system, you can:
- ✅ Generate hall tickets
- ✅ Scan QR codes during exams
- ✅ Mark attendance
- ✅ View student reports

---

## Getting Help

If CSV upload still fails:
1. Take a screenshot of the error
2. Check the browser console (F12)
3. Check the network response in Developer Tools
4. Note the exact error message
5. Try with the sample file first
