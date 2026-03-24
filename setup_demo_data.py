import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HALLTICKETT.settings')
django.setup()

from django.contrib.auth.models import User
from home.models import AdminUser, Student, Exam, Subject, Room
from datetime import datetime, timedelta

# Create admin users
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@hallticket.com',
        'first_name': 'System',
        'last_name': 'Admin',
        'is_staff': True,
        'is_superuser': True
    }
)
admin_user.set_password('admin123')
admin_user.save()

admin_role, _ = AdminUser.objects.get_or_create(
    user=admin_user,
    defaults={'role': 'SUPER_ADMIN', 'department': 'Administration'}
)

# Create staff user
staff_user, _ = User.objects.get_or_create(
    username='staff',
    defaults={
        'email': 'staff@hallticket.com',
        'first_name': 'Exam',
        'last_name': 'Staff',
        'is_staff': True
    }
)
staff_user.set_password('staff123')
staff_user.save()

staff_role, _ = AdminUser.objects.get_or_create(
    user=staff_user,
    defaults={'role': 'STAFF', 'department': 'Examination'}
)

print("✓ Admin users created")

# Create sample students
students_data = [
    {'roll_number': 'CS101', 'name': 'Alice Johnson', 'email': 'alice@student.com', 'batch': '2024', 'branch': 'Computer Science'},
    {'roll_number': 'CS102', 'name': 'Bob Smith', 'email': 'bob@student.com', 'batch': '2024', 'branch': 'Computer Science'},
    {'roll_number': 'CS103', 'name': 'Carol Williams', 'email': 'carol@student.com', 'batch': '2024', 'branch': 'Computer Science'},
    {'roll_number': 'EC101', 'name': 'David Brown', 'email': 'david@student.com', 'batch': '2024', 'branch': 'Electronics'},
    {'roll_number': 'EC102', 'name': 'Eve Davis', 'email': 'eve@student.com', 'batch': '2024', 'branch': 'Electronics'},
]

for data in students_data:
    student, created = Student.objects.get_or_create(
        roll_number=data['roll_number'],
        defaults=data
    )
    if created:
        print(f"✓ Created student: {student.name}")

print("✓ Sample students created")

# Create sample subjects
subjects_data = [
    {'code': 'CS201', 'name': 'Data Structures'},
    {'code': 'CS202', 'name': 'Algorithms'},
    {'code': 'CS203', 'name': 'Operating Systems'},
    {'code': 'EC201', 'name': 'Digital Electronics'},
    {'code': 'MA101', 'name': 'Engineering Mathematics'},
]

for data in subjects_data:
    Subject.objects.get_or_create(code=data['code'], defaults={'name': data['name']})

print("✓ Sample subjects created")

# Create sample rooms
rooms_data = [
    {'room_number': 'A101', 'rows': 10, 'cols': 6, 'capacity': 60},
    {'room_number': 'A102', 'rows': 10, 'cols': 6, 'capacity': 60},
    {'room_number': 'B101', 'rows': 8, 'cols': 5, 'capacity': 40},
    {'room_number': 'B102', 'rows': 8, 'cols': 5, 'capacity': 40},
    {'room_number': 'AUDI-01', 'rows': 15, 'cols': 10, 'capacity': 150},
]

for data in rooms_data:
    Room.objects.get_or_create(room_number=data['room_number'], defaults=data)

print("✓ Sample rooms created")

# Create sample exams
today = datetime.now()
exams_data = [
    {
        'subject_code': 'CS201',
        'subject_name': 'Data Structures',
        'date': (today + timedelta(days=5)).date(),
        'start_time': '09:00',
        'end_time': '11:00',
        'room_number': 'A101',
        'invigilator_name': 'Prof. John Doe',
        'max_students': 50
    },
    {
        'subject_code': 'CS202',
        'subject_name': 'Algorithms',
        'date': (today + timedelta(days=6)).date(),
        'start_time': '14:00',
        'end_time': '16:00',
        'room_number': 'A102',
        'invigilator_name': 'Prof. Jane Smith',
        'max_students': 50
    },
    {
        'subject_code': 'EC201',
        'subject_name': 'Digital Electronics',
        'date': (today + timedelta(days=7)).date(),
        'start_time': '09:00',
        'end_time': '11:00',
        'room_number': 'B101',
        'invigilator_name': 'Prof. Mike Johnson',
        'max_students': 40
    },
]

for data in exams_data:
    exam, created = Exam.objects.get_or_create(
        subject_code=data['subject_code'],
        defaults=data
    )
    if created:
        print(f"✓ Created exam: {exam.subject_name}")

print("✓ Sample exams created")
print("\n✅ Database initialization complete!")
print("\nDemo Credentials:")
print("  Admin: admin / admin123")
print("  Staff: staff / staff123")
print("  Students: Use roll numbers (CS101, CS102, etc.)")
