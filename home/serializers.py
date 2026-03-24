from rest_framework import serializers
from django.contrib.auth.models import User
from home.models import Student, Exam, HallTicket, Attendance, AdminUser, Subject, Room
import csv
from io import StringIO

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class AdminUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AdminUser
        fields = ['id', 'user', 'role', 'department', 'created_at']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'


class HallTicketListSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)
    qr_code_url = serializers.SerializerMethodField()
    
    is_present = serializers.SerializerMethodField()
    
    class Meta:
        model = HallTicket
        fields = ['id', 'ticket_number', 'student', 'exam', 'status', 'seat_assigned', 'is_present', 'qr_code_url', 'issued_at']
    
    def get_is_present(self, obj):
        return Attendance.objects.filter(hall_ticket=obj).exists()
    
    def get_qr_code_url(self, obj):
        request = self.context.get('request')
        if obj.qr_code and request:
            return request.build_absolute_uri(obj.qr_code.url)
        return None


class HallTicketDetailSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)
    qr_code_url = serializers.SerializerMethodField()
    qr_data = serializers.SerializerMethodField()
    
    class Meta:
        model = HallTicket
        fields = '__all__'
    
    def get_qr_code_url(self, obj):
        request = self.context.get('request')
        if obj.qr_code and request:
            return request.build_absolute_uri(obj.qr_code.url)
        return None
    
    def get_qr_data(self, obj):
        return obj.get_qr_data()


class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'


class BulkStudentUploadSerializer(serializers.Serializer):
    csv_file = serializers.FileField()
    
    def validate_csv_file(self, file):
        if not file.name.endswith('.csv'):
            raise serializers.ValidationError("File must be in CSV format (.csv)")
        
        # Check file size (max 5MB)
        if file.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("CSV file must be smaller than 5MB")
        
        return file
    
    def create(self, validated_data):
        csv_file = validated_data['csv_file']
        
        try:
            csv_data = csv_file.read()
            # Try UTF-8 first, then fall back to other encodings
            try:
                csv_data = csv_data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    csv_data = csv_data.decode('iso-8859-1')
                except UnicodeDecodeError:
                    csv_data = csv_data.decode('latin-1')
        except Exception as e:
            raise serializers.ValidationError(f"Error reading CSV file: {str(e)}")
        
        try:
            csv_reader = csv.DictReader(StringIO(csv_data))
            
            if not csv_reader.fieldnames:
                raise serializers.ValidationError("CSV file is empty or has no headers")
            
            # Validate required fields
            required_fields = {'roll_number', 'name', 'email'}
            missing_fields = required_fields - set(csv_reader.fieldnames)
            if missing_fields:
                raise serializers.ValidationError(
                    f"CSV is missing required columns: {', '.join(sorted(missing_fields))}"
                )
            
            created_count = 0
            updated_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start from 2 (after header)
                try:
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                        
                    # Check for required fields
                    roll_num = row.get('roll_number', '').strip()
                    name = row.get('name', '').strip()
                    email = row.get('email', '').strip()
                    
                    if not roll_num or not name or not email:
                        errors.append(f"Row {row_num}: Missing required fields (roll_number, name, email)")
                        continue
                    
                    # Validate email format
                    if '@' not in email or '.' not in email.split('@')[-1]:
                        errors.append(f"Row {row_num}: Invalid email format '{email}'")
                        continue
                    
                    # Check if student with this roll number already exists
                    existing_student = Student.objects.filter(roll_number=roll_num).first()
                    
                    if existing_student:
                        # Student exists, update if needed
                        existing_student.name = name
                        existing_student.email = email
                        existing_student.phone = row.get('phone', '').strip()
                        existing_student.gender = row.get('gender', 'M').strip() or 'M'
                        existing_student.batch = row.get('batch', '').strip()
                        existing_student.branch = row.get('branch', '').strip()
                        existing_student.save()
                        updated_count += 1
                    else:
                        # Create new student
                        student = Student.objects.create(
                            roll_number=roll_num,
                            name=name,
                            email=email,
                            phone=row.get('phone', '').strip(),
                            gender=row.get('gender', 'M').strip() or 'M',
                            batch=row.get('batch', '').strip(),
                            branch=row.get('branch', '').strip(),
                        )
                        created_count += 1
                        
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            return {
                'success': True,
                'created': created_count,
                'updated': updated_count,
                'errors': errors,
                'total_processed': created_count + updated_count + len(errors)
            }
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(f"Error processing CSV: {str(e)}")
