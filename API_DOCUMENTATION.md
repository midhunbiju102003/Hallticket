# 📚 API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication

### Login (Admin/Staff)
```http
POST /login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123",
  "role": "admin"  // or "staff"
}

Response:
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@hallticket.com",
    "role": "SUPER_ADMIN"
  }
}
```

### Student Login
```http
POST /student-login/
Content-Type: application/json

{
  "roll_number": "CS101"
}

Response:
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "student": {
    "id": "uuid-here",
    "roll_number": "CS101",
    "name": "Alice Johnson",
    "email": "alice@student.com",
    "batch": "2024",
    "branch": "Computer Science"
  }
}
```

### Using Token
All subsequent requests must include:
```
Authorization: Bearer <token_here>
```

---

## Students API

### List All Students
```http
GET /students/
Authorization: Bearer <token>

Response:
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "roll_number": "CS101",
      "name": "Alice Johnson",
      "email": "alice@student.com",
      "phone": "9876543210",
      "gender": "M",
      "batch": "2024",
      "branch": "Computer Science",
      "photo": null,
      "created_at": "2024-02-19T10:30:00Z"
    }
  ]
}
```

### Get Student Details
```http
GET /students/{student_id}/
Authorization: Bearer <token>

Response:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "roll_number": "CS101",
  "name": "Alice Johnson",
  "email": "alice@student.com",
  "phone": "9876543210",
  "gender": "M",
  "batch": "2024",
  "branch": "Computer Science",
  "created_at": "2024-02-19T10:30:00Z"
}
```

### Create Student
```http
POST /students/
Authorization: Bearer <token>
Content-Type: application/json

{
  "roll_number": "CS104",
  "name": "David Johnson",
  "email": "david@student.com",
  "phone": "9876543212",
  "gender": "M",
  "batch": "2024",
  "branch": "Computer Science"
}

Response: (201 Created)
Same as Get Student Details
```

### Search Students
```http
GET /students/search/?q=CS101
Authorization: Bearer <token>

Response:
{
  "results": [
    { /* student object */ }
  ]
}
```

### Bulk Upload Students (CSV)
```http
POST /students/bulk_upload/
Authorization: Bearer <token>
Content-Type: multipart/form-data

csv_file: <file.csv>

CSV Format:
roll_number,name,email,phone,gender,batch,branch
CS101,Alice,alice@student.com,9876543210,M,2024,CS
CS102,Bob,bob@student.com,9876543211,M,2024,CS

Response:
{
  "success": true,
  "created": 2,
  "errors": []
}
```

---

## Exams API

### List All Exams
```http
GET /exams/
GET /exams/?date_from=2024-02-25&date_to=2024-02-28
Authorization: Bearer <token>

Response:
{
  "count": 3,
  "results": [
    {
      "id": "550e8400-...",
      "subject_code": "CS201",
      "subject_name": "Data Structures",
      "date": "2024-02-25",
      "start_time": "09:00:00",
      "end_time": "11:00:00",
      "room_number": "A101",
      "invigilator_name": "Prof. Smith",
      "max_students": 50,
      "created_at": "2024-02-19T10:00:00Z"
    }
  ]
}
```

### Get Exam Details
```http
GET /exams/{exam_id}/
Authorization: Bearer <token>

Response:
Same format as list item above
```

### Create Exam
```http
POST /exams/
Authorization: Bearer <token>
Content-Type: application/json

{
  "subject_code": "CS301",
  "subject_name": "Operating Systems",
  "date": "2024-03-01",
  "start_time": "09:00",
  "end_time": "11:00",
  "room_number": "A102",
  "invigilator_name": "Prof. Johnson",
  "max_students": 45
}

Response: (201 Created)
Same format as Get Exam Details
```

---

## Hall Tickets API

### List Hall Tickets
```http
GET /hall-tickets/
GET /hall-tickets/?student_id=uuid&exam_id=uuid
Authorization: Bearer <token>

Response:
{
  "count": 5,
  "results": [
    {
      "id": "550e8400-...",
      "ticket_number": "CS201-CS101-1708361400.01",
      "student": { /* student object */ },
      "exam": { /* exam object */ },
      "status": "ACTIVE",
      "qr_code_url": "http://localhost:8000/media/qr_codes/hallticket_CS201-CS101.png",
      "issued_at": "2024-02-19T10:30:00Z"
    }
  ]
}
```

### Get Hall Ticket Details
```http
GET /hall-tickets/{ticket_id}/
Authorization: Bearer <token>

Response:
{
  "id": "550e8400-...",
  "ticket_number": "CS201-CS101-...",
  "student": { /* full student object */ },
  "exam": { /* full exam object */ },
  "qr_code": "media/qr_codes/hallticket_...",
  "qr_code_url": "http://localhost:8000/media/qr_codes/...",
  "qr_data": "HT:ticket_number:roll_number:subject_code",
  "signature": "abcd1234...",
  "status": "ACTIVE",
  "issued_at": "2024-02-19T10:30:00Z"
}
```

### Generate Bulk Hall Tickets
```http
POST /hall-tickets/generate_bulk/
Authorization: Bearer <token>
Content-Type: application/json

{
  "exam_id": "550e8400-e29b-41d4-a716-446655440000",
  "student_ids": [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002",
    "550e8400-e29b-41d4-a716-446655440003"
  ]
}

Response:
{
  "success": true,
  "created": 3,
  "failed": []
}
```

### Download Hall Ticket PDF
```http
GET /hall-tickets/{ticket_id}/download_pdf/
Authorization: Bearer <token>

Response: (application/pdf)
[Binary PDF file content]
```

### Get QR Code Image
```http
GET /hall-tickets/{ticket_id}/get_qr_image/
Authorization: Bearer <token>

Response: (image/png)
[Binary PNG image content]
```

---

## Attendance API

### Mark Attendance via QR Scan
```http
POST /attendance/mark_attendance/
Authorization: Bearer <token>
Content-Type: application/json

{
  "qr_data": "HT:ticket_number:CS101:CS201",
  "exam_id": "550e8400-...",
  "device": "WEB_SCANNER"
}

Response:
{
  "success": true,
  "message": "Attendance marked successfully",
  "status": "VALID",
  "attendance": { /* attendance object */ },
  "student": { /* student object */ }
}

OR (if already scanned):
{
  "success": true,
  "message": "Already scanned",
  "status": "ALREADY_SCANNED",
  "attendance": { /* attendance object */ }
}

OR (if invalid):
{
  "success": false,
  "message": "Invalid hall ticket",
  "status": "INVALID"
}
```

### List Attendance Records
```http
GET /attendance/
GET /attendance/?exam_id=550e8400-...
Authorization: Bearer <token>

Response:
{
  "count": 45,
  "results": [
    {
      "id": "550e8400-...",
      "hall_ticket": { /* ticket object */ },
      "exam": { /* exam object */ },
      "student": { /* student object */ },
      "status": "PRESENT",
      "scanned_at": "2024-02-25T09:15:30Z",
      "scanned_by": "staff",
      "scanned_device": "WEB_SCANNER"
    }
  ]
}
```

### Get Exam Report
```http
GET /attendance/exam_report/?exam_id=550e8400-...
Authorization: Bearer <token>

Response:
{
  "exam": { /* exam object */ },
  "total_tickets": 50,
  "marked_attendance": 45,
  "attendance_breakdown": [
    {
      "status": "PRESENT",
      "count": 42
    },
    {
      "status": "LATE",
      "count": 3
    },
    {
      "status": "ABSENT",
      "count": 5
    }
  ]
}
```

---

## Admin Users API

### List Admin Users
```http
GET /admin-users/
Authorization: Bearer <token>

Response:
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@hallticket.com",
        "first_name": "System",
        "last_name": "Admin"
      },
      "role": "SUPER_ADMIN",
      "department": "Administration",
      "created_at": "2024-02-19T10:00:00Z"
    }
  ]
}
```

### Create Admin User
```http
POST /admin-users/
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 3,
  "role": "STAFF",
  "department": "Examination"
}

Response: (201 Created)
Same format as list item
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "message": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid token or credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Not found"
}
```

### 500 Server Error
```json
{
  "success": false,
  "message": "Internal server error"
}
```

---

## Status Codes Reference

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request succeeded, no return data |
| 400 | Bad Request - Invalid data |
| 401 | Unauthorized - No valid token |
| 403 | Forbidden - No permission |
| 404 | Not Found - Resource doesn't exist |
| 500 | Server Error - Internal error |

---

## Rate Limiting

Currently no rate limiting. For production, add:
```bash
pip install django-ratelimit
```

---

## CORS Headers

Requests include standard CORS headers for cross-origin requests:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

**For more details, refer to README.md and SETUP_GUIDE.md**
