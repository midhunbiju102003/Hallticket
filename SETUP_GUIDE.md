# 🚀 Quick Setup Guide

## Installation Steps

### Step 1: Navigate to Project
```bash
cd "c:\Users\midhu\OneDrive\Desktop\Hallticket\HALLTICKETT"
```

### Step 2: Activate Virtual Environment (if needed)
```bash
..\H-T\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install django djangorestframework django-cors-headers python-decouple qrcode[pil] reportlab PyJWT djangorestframework-simplejwt pillow
```

### Step 4: Apply Migrations
```bash
python manage.py migrate
```

### Step 5: Create Admin User (Optional - Demo exists)
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123
```

### Step 6: Run Server
```bash
python manage.py runserver
```

### Step 7: Access Application
- Main: http://localhost:8000
- Admin: username=admin, password=admin123
- Staff: username=staff, password=staff123
- Student: Roll# (CS101, CS102, CS103)

## 📱 User Workflows

### Admin Workflow
1. Login with admin credentials
2. Click "Add Exam" →  Fill details → Save
3. Click "Upload CSV" or "Add Student" → Add students
4. Select Exam → Select Students → "Generate Tickets"
5. Students get QR codes & tickets

### Student Workflow
1. Login with roll number (CS101)
2. View "My Hall Tickets" section
3. Click "Download PDF" to get printable ticket
4. Print ticket before exam day

### Staff Workflow
1. Login with staff credentials
2. Select exam from dropdown
3. Click "Start" to start camera
4. Position QR code in camera
5. System automatically marks attendance
6. View real-time stats on right panel
7. Click "Export Report" when done

## 🎯 Common Tasks

### Add New Exam
- Admin Dashboard → Exam Management Section
- Fill: Subject Code, Name, Date, Time, Room, Invigilator
- Click "Add Exam"

### Bulk Upload Students
- Admin Dashboard → Upload CSV
- Use format: roll_number, name, email, phone, gender, batch, branch
- Select file → Click Upload

### Generate Hall Tickets
- Admin Dashboard → Hall Ticket Generation
- Select Exam from dropdown
- Click "Select Students" (select count)
- Click "Generate Tickets"
- Each ticket gets unique QR code + signature

### Mark Attendance
- Staff Login → Scanner Page
- Select exam
- Click "Start" (allow camera permission)
- Scan or manually paste QR codes
- Real-time report updates
- Export CSV when done

## ⚡ API Quick Reference

### Login (Get JWT Token)
```bash
POST http://localhost:8000/api/login/
{
  "username": "admin",
  "password": "admin123",
  "role": "admin"
}
```

### List Students
```bash
GET http://localhost:8000/api/students/
Header: Authorization: Bearer <TOKEN>
```

### Create Exam
```bash
POST http://localhost:8000/api/exams/
{
  "subject_code": "CS201",
  "subject_name": "Data Structures",
  "date": "2024-02-25",
  "start_time": "09:00",
  "end_time": "11:00",
  "room_number": "A101",
  "invigilator_name": "Prof. Smith",
  "max_students": 50
}
```

### Generate Hall Tickets
```bash
POST http://localhost:8000/api/hall-tickets/generate_bulk/
{
  "exam_id": "exam-uuid-here",
  "student_ids": ["student-id-1", "student-id-2"]
}
```

### Mark Attendance
```bash
POST http://localhost:8000/api/attendance/mark_attendance/
{
  "qr_data": "HT:TICKET001:CS101:CS201",
  "exam_id": "exam-uuid",
  "device": "WEB_SCANNER"
}
```

## 📊 Testing Data

**Exams Created:**
- CS201: Data Structures (5 days from today, 9:00 AM)
- CS202: Algorithms (6 days from today, 2:00 PM)
- EC201: Digital Electronics (7 days from today, 9:00 AM)

**Students Created:**
- CS101: Alice Johnson
- CS102: Bob Smith
- CS103: Carol Williams

## 🔧 Useful Django Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Open Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser

# Run tests (if created)
python manage.py test

# Collect static files (production)
python manage.py collectstatic

# Start server on custom port
python manage.py runserver 0.0.0.0:8080
```

## 🐛 Debug Tips

### Enable Django Debug Toolbar
```bash
pip install django-debug-toolbar
# Add to INSTALLED_APPS: 'debug_toolbar'
# Add to MIDDLEWARE:  'debug_toolbar.middleware.DebugToolbarMiddleware'
```

### View Database Queries
```python
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as context:
    # Your code here
    pass
print(context.captured_queries)
```

### Check Active Routes
```bash
python manage.py show_urls
```

## 📌 Important Notes

1. **Database**: Currently uses SQLite (fine for demo, use PostgreSQL for production)
2. **Media Files**: Stored in `media/` folder locally
3. **QR Codes**: Generated as PNG images, stored in `media/qr_codes/`
4. **PDFs**: Generated on-the-fly, not stored
5. **Static Files**: Served from `static/` folder
6. **Tokens**: JWT tokens expire after 24 hours

## 🔒 Security Checklist

- [ ] Change admin password from demo default
- [ ] Update SECRET_KEY in settings.py
- [ ] Set DEBUG=False for production
- [ ] Configure ALLOWED_HOSTS
- [ ] Use HTTPS in production
- [ ] Set up proper logging
- [ ] Configure email backend for notifications
- [ ] Regular database backups
- [ ] Monitor log files for errors

## 🎓 Learning Resources

- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- Tailwind CSS: https://tailwindcss.com/
- html5-qrcode: https://github.com/mebjas/html5-qrcode

---

**Ready to Go! 🚀**

If you encounter any issues:
1. Check README.md for full documentation
2. Review troubleshooting section
3. Check browser console for frontend errors (F12)
4. Check server console for backend errors
