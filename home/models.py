from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import hmac
import hashlib

class Student(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    roll_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=False, blank=False)  # Removed unique constraint
    phone = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    batch = models.CharField(max_length=50, blank=True, db_index=True)  # Made indexed for filtering
    branch = models.CharField(max_length=100, blank=True, db_index=True) # Made indexed for filtering
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['roll_number']
    
    def __str__(self):
        return f"{self.roll_number} - {self.name}"


class Subject(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Room(models.Model):
    room_number = models.CharField(max_length=50, unique=True)
    capacity = models.IntegerField(default=60)
    rows = models.IntegerField(default=10)
    cols = models.IntegerField(default=6)

    def __str__(self):
        return f"Room {self.room_number}"


class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject_code = models.CharField(max_length=50, db_index=True)
    subject_name = models.CharField(max_length=200)
    date = models.DateField(db_index=True)
    start_time = models.TimeField(db_index=True)
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50)
    invigilator_name = models.CharField(max_length=200)
    max_students = models.IntegerField()
    # Hall Layout
    hall_rows = models.IntegerField(default=10)
    hall_cols = models.IntegerField(default=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"


class HallTicket(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='hall_tickets')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='hall_tickets')
    
    # Secure QR Code Data
    ticket_number = models.CharField(max_length=100, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/')
    signature = models.CharField(max_length=256)  # HMAC signature for validation
    seat_assigned = models.CharField(max_length=10, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    issued_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        unique_together = ('student', 'exam')
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.exam.subject_code}"
    
    def get_qr_data(self):
        """Generate Master Student QR code data (valid for all student's exams)"""
        return f"ST:{self.student.roll_number}"
    
    def generate_signature(self, secret_key='hall_ticket_secret'):
        """Generate HMAC signature for validation based on student roll number"""
        data = self.get_qr_data()
        return hmac.new(
            secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def is_valid_signature(self, provided_signature, secret_key='hall_ticket_secret'):
        """Validate if signature is correct"""
        expected_signature = self.generate_signature(secret_key)
        return hmac.compare_digest(expected_signature, provided_signature)


class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hall_ticket = models.ForeignKey(HallTicket, on_delete=models.CASCADE, related_name='attendance_records')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('PRESENT', 'Present'),
            ('ABSENT', 'Absent'),
            ('LATE', 'Late'),
        ],
        default='PRESENT'
    )
    scanned_at = models.DateTimeField(auto_now_add=True, db_index=True)
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    scanned_device = models.CharField(max_length=100, blank=True)
    
    class Meta:
        unique_together = ('hall_ticket', 'exam')
        ordering = ['-scanned_at']
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.exam.subject_code} - {self.status}"


class AdminUser(models.Model):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('ADMIN', 'Admin'),
        ('STAFF', 'Exam Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ADMIN')
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
