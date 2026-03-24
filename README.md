# 🎓 Hall Ticket Management System

A complete web-based examination hall ticket management system with QR code generation, PDF download, and real-time attendance tracking via camera QR scanning.

## 🌟 Features

### ✅ Admin Portal
- Add students individually or bulk upload via CSV
- Create and manage exams
- Generate hall tickets with QR codes
- Download hall tickets as PDF
- View attendance reports and statistics
- Manage staff users

### ✅ Student Portal
- Login with roll number (no password required for demo)
- View assigned exams
- Download hall tickets as PDF
- View exam schedule
- Check attendance status

### ✅ Staff Verification Portal
- Real-time QR code scanning via camera (WebRTC)
- Manual QR code entry support
- Instant attendance marking
- Invalid ticket detection
- Duplicate scan prevention
- Daily attendance report export

### ✅ Security Features
- JWT token-based authentication
- HMAC signature validation for QR codes
- Role-based access control (Admin, Staff, Student)
- Secure ticket verification

## 🏗️ System Architecture

```
Frontend (HTML/Tailwind CSS)
    ├── Admin Dashboard
    ├── Student Portal
    └── Staff Scanner
        ↓
REST API (Django)
    ├── Authentication
    ├── Student Management
    ├── Exam Management
    ├── Hall Ticket Generation
    └── Attendance Logging
        ↓
Database (SQLite)
    ├── Users & Roles
    ├── Students
    ├── Exams
    ├── Hall Tickets
    └── Attendance
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual Environment (Recommended)

### Installation

1. **Activate Virtual Environment**
```bash

H-T\Scripts\activate  # On Windows
```

2. **Install Dependencies**
```bash
pip install django djangorestframework python-decouple qrcode[pil] reportlab PyJWT django-cors-headers pillow
```

3. **Setup Database**
```bash
cd HALLTICKETT
python manage.py makemigrations
python manage.py migrate
```

4. **Create Demo Data**
```bash
python manage.py shell -c "
from django.contrib.auth.models import User
from home.models import AdminUser, Student

# Create admin user
u, _ = User.objects.get_or_create(username='admin')
u.set_password('admin123')
u.is_staff = True
u.is_superuser = True
u.save()
AdminUser.objects.get_or_create(user=u, defaults={'role': 'SUPER_ADMIN'})

# Create staff user
s, _ = User.objects.get_or_create(username='staff')
s.set_password('staff123')
s.is_staff = True
s.save()
AdminUser.objects.get_or_create(user=s, defaults={'role': 'STAFF'})

# Create sample students
from datetime import datetime, timedelta
students = [
    {'roll_number': 'CS101', 'name': 'Alice Johnson', 'email': 'alice@student.com', 'batch': '2024', 'branch': 'CS'},
    {'roll_number': 'CS102', 'name': 'Bob Smith', 'email': 'bob@student.com', 'batch': '2024', 'branch': 'CS'},
    {'roll_number': 'CS103', 'name': 'Carol Williams', 'email': 'carol@student.com', 'batch': '2024', 'branch': 'CS'},
]
for data in students:
    Student.objects.get_or_create(roll_number=data['roll_number'], defaults=data)

print('✓ Demo data created!')
"
```

5. **Start Server**
```bash
python manage.py runserver
```

6. **Access Application**
- Open browser to: `http://localhost:8000`
- Admin Login: `admin` / `admin123`
- Staff Login: `staff` / `staff123`
- Student Login: Use roll numbers like `CS101`

## 📋 Demo Credentials

| Role | Username | Password | Access |
|------|----------|----------|--------|
| Super Admin | admin | admin123 | http://localhost:8000/admin/dashboard/ |
| Exam Staff | staff | staff123 | http://localhost:8000/staff/scanner/ |
| Student | CS101/CS102/CS103 | (Auto) | http://localhost:8000/student/portal/ |

## 📋 CSV Import Format

For bulk student import, use this CSV format:

```csv
roll_number,name,email,phone,gender,batch,branch
CS101,Alice Johnson,alice@student.com,9876543210,M,2024,Computer Science
CS102,Bob Smith,bob@student.com,9876543211,M,2024,Computer Science
CS103,Carol Williams,carol@student.com,9876543212,F,2024,Computer Science
```

## 🔧 API Endpoints

### Authentication
```
POST /api/login/
  Body: {"username": "admin", "password": "admin123", "role": "admin"}
  
POST /api/student-login/
  Body: {"roll_number": "CS101"}
```

### Students
```
GET    /api/students/                    # List all students
POST   /api/students/                    # Create student
GET    /api/students/{id}/               # Get student details
POST   /api/students/bulk_upload/        # Upload CSV
GET    /api/students/search/?q=CS101     # Search students
```

### Exams
```
GET    /api/exams/                       # List exams
POST   /api/exams/                       # Create exam
GET    /api/exams/{id}/                  # Get exam details
```

### Hall Tickets
```
GET    /api/hall-tickets/                          # List tickets
POST   /api/hall-tickets/                          # Create ticket
GET    /api/hall-tickets/{id}/                    # Get ticket details
POST   /api/hall-tickets/generate_bulk/           # Bulk generate
GET    /api/hall-tickets/{id}/download_pdf/       # Download PDF
GET    /api/hall-tickets/{id}/get_qr_image/       # Get QR code
```

### Attendance
```
POST   /api/attendance/mark_attendance/           # Mark attendance
GET    /api/attendance/                           # List attendance
GET    /api/attendance/exam_report/?exam_id={}    # Exam report
```

## 🎯 Workflow

### 1. Admin Setup
1. Login to admin dashboard
2. Add exams (e.g., "Data Structures", Date, Time, Room)
3. Add students (individual or bulk CSV upload)

### 2. Hall Ticket Generation
1. Select exam from dropdown
2. Select students to generate for
3. Click "Generate Tickets"
4. System generates QR codes and stores them

### 3. Student Access
1. Student logs in with roll number
2. Views assigned exams and hall tickets
3. Downloads PDF for printing

### 4. Exam Day - Attendance
1. Staff opens scanner page
2. Selects the exam
3. Starts camera scanner
4. Scans QR codes from printed hall tickets
5. System marks attendance instantly
6. Export report when done

## 📁 Project Structure

```
HALLTICKETT/
├── manage.py
├── db.sqlite3
├── HALLTICKETT/
│   ├── settings.py          # Configuration
│   ├── urls.py              # Main URL config
│   └── wsgi.py
├── home/
│   ├── models.py            # Database models
│   ├── views.py             # API views
│   ├── serializers.py       # DRF serializers
│   ├── urls.py              # App URLs
│   ├── qr_utils.py          # QR generation
│   ├── pdf_utils.py         # PDF generation
│   └── migrations/
├── templates/
│   ├── base.html            # Base template
│   ├── login.html           # Login page
│   ├── admin/
│   │   └── dashboard.html   # Admin dashboard
│   ├── student/
│   │   └── portal.html      # Student portal
│   └── staff/
│       └── scanner.html     # QR scanner
├── static/                  # CSS, JS files
└── media/                   # Uploaded files
    ├── qr_codes/
    └── student_photos/
```

## 🔐 Security Considerations

1. **QR Code Validation**: Each QR code contains an HMAC signature that's validated server-side
2. **JWT Tokens**: Used for stateless authentication with 24-hour expiry
3. **CSRF Protection**: Enabled by default in Django
4. **Permission Checks**: Role-based access control on all endpoints
5. **Duplicate Prevention**: Same ticket can't be scanned twice for same exam

## 🌐 Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| QR Scanner | ✓ | ✓ | ✓ | ✓ |
| PDF Download | ✓ | ✓ | ✓ | ✓ |
| CSV Upload | ✓ | ✓ | ✓ | ✓ |
| Responsive UI | ✓ | ✓ | ✓ | ✓ |

## 📊 Database Models

### Student
```python
- id (UUID)
- roll_number (Unique)
- name
- email
- phone
- gender
- batch
- branch
- photo (Optional)
```

### Exam
```python
- id (UUID)
- subject_code (Unique)
- subject_name
- date
- start_time / end_time
- room_number
- invigilator_name
- max_students
```

### HallTicket
```python
- id (UUID)
- student (FK)
- exam (FK)
- ticket_number (Unique)
- qr_code (Image)
- signature (HMAC validation)
- status (ACTIVE/CANCELLED/COMPLETED)
```

### Attendance
```python
- id (UUID)
- hall_ticket (FK)
- exam (FK)
- student (FK)
- status (PRESENT/ABSENT/LATE)
- scanned_at
- scanned_by
- scanned_device
```

## 🚧 Troubleshooting

### Issue: "No such table" error
```bash
python manage.py migrate
```

### Issue: QR Scanner not working
- Check browser permissions for camera access
- Try manual QR entry option
- Ensure camera is working

### Issue: CORS errors
- Check CORS_ALLOWED_ORIGINS in settings.py
- Add your frontend URL if different from localhost

### Issue: PDF generation fails
- Ensure reportlab is installed: `pip install reportlab`
- Check file permissions for media folder

## 🔄 Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Update ALLOWED_HOSTS with your domain
3. Use PostgreSQL instead of SQLite
4. Set SECRET_KEY environment variable
5. Configure static files with WhiteNoise or CloudFront
6. Use Gunicorn/uWSGI as application server
7. Set up HTTPS with SSL certificate

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check Django/DRF documentation
4. Verify database migrations are applied

## 📝 License

This project is provided as-is for educational purposes.

## 🙏 Acknowledgments

Built with:
- Django & Django REST Framework
- Tailwind CSS
- html5-qrcode
- ReportLab
- PyJWT

---

**Made with ❤️ for secure examination management**
