from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Q, Count
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
import jwt
import json
from datetime import datetime, timedelta

from home.models import Student, Exam, HallTicket, Attendance, AdminUser, Subject, Room
from home.serializers import (
    StudentSerializer, ExamSerializer, HallTicketListSerializer,
    HallTicketDetailSerializer, AttendanceSerializer, AdminUserSerializer,
    BulkStudentUploadSerializer, UserSerializer, SubjectSerializer, RoomSerializer
)
from home.qr_utils import create_hall_ticket_qr
from home.pdf_utils import create_hall_ticket_pdf


# ==================== AUTHENTICATION VIEWS ====================

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """User login endpoint"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'admin')  # admin, student, staff
        
        user = User.objects.filter(username=username).first()
        if not user or not user.check_password(password):
            return JsonResponse({'success': False, 'message': 'Invalid credentials'}, status=401)
        
        # Check user role - allow both SUPER_ADMIN and role-specific access
        admin_user = AdminUser.objects.filter(user=user).first()
        if not admin_user:
            return JsonResponse({'success': False, 'message': 'User is not authorized'}, status=403)
        
        # Allow SUPER_ADMIN and role-specific access
        if role.lower() == 'admin':
            if admin_user.role not in ['SUPER_ADMIN', 'ADMIN']:
                return JsonResponse({'success': False, 'message': 'Invalid admin credentials'}, status=403)
        elif role.lower() == 'staff':
            if admin_user.role not in ['SUPER_ADMIN', 'STAFF']:
                return JsonResponse({'success': False, 'message': 'Invalid staff credentials'}, status=403)
        
        # Create Django session for this user (for SessionAuthentication)
        from django.contrib.auth import login as django_login
        django_login(request, user)
        
        # Generate JWT token for frontend use
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': admin_user.role,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, 'hall_ticket_secret', algorithm='HS256')
        
        return JsonResponse({
            'success': True,
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': admin_user.role
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def student_login_view(request):
    """Student login with roll number"""
    try:
        data = json.loads(request.body)
        roll_number = data.get('roll_number')
        
        student = Student.objects.filter(roll_number=roll_number).first()
        if not student:
            return JsonResponse({'success': False, 'message': 'Student not found'}, status=404)
        
        # Generate JWT token for student
        payload = {
            'student_id': str(student.id),
            'roll_number': student.roll_number,
            'name': student.name,
            'email': student.email,
            'batch': student.batch,
            'branch': student.branch,
            'role': 'STUDENT',
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, 'hall_ticket_secret', algorithm='HS256')
        
        return JsonResponse({
            'success': True,
            'token': token,
            'student': StudentSerializer(student).data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET"])
@action(detail=False, methods=['get']) # For documentation if needed, but it's a separate path
def api_status(request):
    """Check API status and database connectivity with full stats"""
    # Note: Since this is a plain Django view, it doesn't automatically use DRF auth
    # We'll check the token manually for this specific endpoint or just allow it if needed.
    # But for optimization, let's keep it fast.
    
    try:
        # Optimized count queries
        return JsonResponse({
            'status': 'ok',
            'database': 'connected',
            'stats': {
                'students': Student.objects.count(),
                'exams': Exam.objects.count(),
                'hall_tickets': HallTicket.objects.count(),
                'attendance': Attendance.objects.count(),
                'subjects': Subject.objects.count(),
                'rooms': Room.objects.count()
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'database': 'disconnected',
            'message': str(e)
        }, status=500)


# ==================== STUDENT VIEWSET ====================

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create a new student with logging"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Creating student: {request.data.get('roll_number')}")
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            logger.info(f"Student created successfully: {request.data.get('roll_number')}")
        return response
    
    @action(detail=False, methods=['post'], parser_classes=(MultiPartParser, FormParser))
    def bulk_upload(self, request):
        """Upload students from CSV file"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Bulk upload request received. User: {request.user}, Authenticated: {request.user.is_authenticated}")
            
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'errors': {'csv_file': ['Authentication required. Please login first.']}
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if not request.FILES.get('csv_file'):
                return Response({
                    'success': False,
                    'errors': {'csv_file': ['No CSV file provided']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = BulkStudentUploadSerializer(data=request.data)
            if serializer.is_valid():
                result = serializer.save()
                logger.info(f"Bulk upload successful. Created: {result['created']}, Updated: {result['updated']}")
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                # Extract the first error message for clarity
                error_messages = []
                for field, errors in serializer.errors.items():
                    logger.warning(f"Validation error in field '{field}': {errors}")
                    if isinstance(errors, list):
                        error_messages.extend(errors)
                    else:
                        error_messages.append(str(errors))
                
                return Response({
                    'success': False,
                    'errors': {
                        'csv_file': error_messages[0] if error_messages else 'Invalid CSV file'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in bulk_upload: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'errors': {
                    'csv_file': f'Server error: {str(e)}'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search students by roll number or name"""
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response({'results': []})
        
        students = Student.objects.filter(
            Q(roll_number__icontains=query) |
            Q(name__icontains=query)
        )[:10]
        
        serializer = StudentSerializer(students, many=True)
        return Response({'results': serializer.data})


# ==================== EXAM VIEWSET ====================

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Exam.objects.all()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        return queryset


# ==================== HALL TICKET VIEWSET ====================

class HallTicketViewSet(viewsets.ModelViewSet):
    queryset = HallTicket.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HallTicketDetailSerializer
        return HallTicketListSerializer
    
    def get_queryset(self):
        queryset = HallTicket.objects.select_related('student', 'exam').all()
        
        # Filter by student if provided
        student_id = self.request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        # Filter by exam if provided
        exam_id = self.request.query_params.get('exam_id')
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def generate_bulk(self, request):
        """Generate hall tickets for multiple students across multiple exams"""
        try:
            exam_ids = request.data.get('exam_ids', [])
            # Support both single exam_id and list exam_ids
            if not exam_ids and request.data.get('exam_id'):
                exam_ids = [request.data.get('exam_id')]
                
            student_ids = request.data.get('student_ids', [])
            
            if not exam_ids:
                return Response({'success': False, 'message': 'No exams selected'}, status=status.HTTP_400_BAD_REQUEST)
            
            results = []
            total_created = 0
            
            for exam_id in exam_ids:
                exam = get_object_or_404(Exam, id=exam_id)
                # Get existing seats for THIS exam
                existing_seats = set(HallTicket.objects.filter(exam=exam).values_list('seat_assigned', flat=True))
                
                exam_created = 0
                exam_failed = []
                
                # Helper for seat generation
                def get_next_seat(row_idx, col_idx, rows, cols, occupied_seats):
                    while row_idx < rows:
                        row_label = chr(65 + row_idx) # A, B, C...
                        seat = f"{row_label}{col_idx + 1}"
                        if seat not in occupied_seats:
                            return seat, row_idx, col_idx
                        
                        col_idx += 1
                        if col_idx >= cols:
                            col_idx = 0
                            row_idx += 1
                    return None, row_idx, col_idx

                current_row = 0
                current_col = 0
                
                # Fetch all students and sort by roll number for systematic seating
                students_to_process = Student.objects.filter(id__in=student_ids).order_by('roll_number')
                
                for student in students_to_process:
                    try:
                        # Check if ticket already exists
                        hall_ticket = HallTicket.objects.filter(student=student, exam=exam).first()
                        
                        if not hall_ticket:
                            # Assign seat
                            seat, next_row, next_col = get_next_seat(current_row, current_col, exam.hall_rows, exam.hall_cols, existing_seats)
                            if not seat:
                                exam_failed.append(f"Student {student.name}: No seats available in hall")
                                continue
                            
                            current_row, current_col = next_row, next_col
                            # Move to next position for next iteration
                            current_col += 1
                            if current_col >= exam.hall_cols:
                                current_col = 0
                                current_row += 1

                            ticket_number = f"{exam.subject_code}-{student.roll_number}-{datetime.now().timestamp()}"
                            hall_ticket = HallTicket.objects.create(
                                student=student,
                                exam=exam,
                                ticket_number=ticket_number,
                                seat_assigned=seat,
                                signature='',
                            )
                            
                            # Generate QR code
                            create_hall_ticket_qr(hall_ticket)
                            
                            # Generate signature
                            hall_ticket.signature = hall_ticket.generate_signature()
                            hall_ticket.save()
                            
                            existing_seats.add(seat)
                            exam_created += 1
                    except Exception as e:
                        exam_failed.append(f"Student {student.id}: {str(e)}")
                
                results.append({
                    'exam': exam.subject_name,
                    'created': exam_created,
                    'failed': exam_failed
                })
                total_created += exam_created
            
            return Response({
                'success': True,
                'total_created': total_created,
                'results': results
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download unified hall ticket with all student's exams as PDF"""
        try:
            hall_ticket = self.get_object()
            student = hall_ticket.student
            
            # Proactively update QR code to ensure it uses the latest Master QR format
            from home.qr_utils import create_hall_ticket_qr
            create_hall_ticket_qr(hall_ticket)
            hall_ticket.signature = hall_ticket.generate_signature()
            hall_ticket.save()
            
            # Fetch all active hall tickets for this student to create a timetable
            all_student_tickets = HallTicket.objects.filter(
                student=student,
                status='ACTIVE'
            ).select_related('exam', 'student')
            
            pdf_buffer = create_hall_ticket_pdf(hall_ticket, all_tickets=all_student_tickets)
            
            filename = f"HallTicket_{student.roll_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"PDF Generation Error: {str(e)}\n{traceback.format_exc()}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def get_qr_image(self, request, pk=None):
        """Get QR code image"""
        try:
            hall_ticket = self.get_object()
            if hall_ticket.qr_code:
                return FileResponse(open(hall_ticket.qr_code.path, 'rb'), content_type='image/png')
            return Response({'error': 'QR code not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==================== ATTENDANCE VIEWSET ====================

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Attendance.objects.select_related('student', 'exam', 'hall_ticket').all()
        
        exam_id = self.request.query_params.get('exam_id')
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def mark_attendance(self, request):
        """Mark attendance via QR code scan"""
        try:
            qr_data = request.data.get('qr_data')
            exam_id = request.data.get('exam_id')
            scanned_device = request.data.get('device', 'WEB')
            
            # Parse QR data: 
            # New format: ST:roll_number
            # Old format: HT:ticket_number:roll_number:subject_code
            parts = qr_data.split(':')
            
            hall_ticket = None
            if parts[0] == 'ST' and len(parts) >= 2:
                # Master QR Format
                roll_number = parts[1]
                hall_ticket = HallTicket.objects.filter(
                    student__roll_number=roll_number,
                    exam_id=exam_id,
                    status='ACTIVE'
                ).first()
                
                if not hall_ticket:
                    return Response({
                        'success': False,
                        'message': f'No active ticket found for student {roll_number} for this session',
                        'status': 'INVALID'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            elif parts[0] == 'HT' and len(parts) == 4:
                # Legacy Ticket-specific Format
                ticket_number = parts[1]
                roll_number = parts[2]
                subject_code = parts[3]
                hall_ticket = HallTicket.objects.filter(
                    ticket_number=ticket_number,
                    student__roll_number=roll_number,
                    exam__subject_code=subject_code,
                    status='ACTIVE'
                ).first()
            
            else:
                # Generic fallback: try treating as roll number directly
                hall_ticket = HallTicket.objects.filter(
                    student__roll_number=qr_data,
                    exam_id=exam_id,
                    status='ACTIVE'
                ).first()
            
            if not hall_ticket:
                return Response({
                    'success': False,
                    'message': 'Invalid verification data or session mismatch',
                    'status': 'INVALID'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if already scanned
            existing_attendance = Attendance.objects.filter(
                hall_ticket=hall_ticket,
                exam_id=exam_id
            ).first()
            
            if existing_attendance:
                return Response({
                    'success': True,
                    'message': 'Already scanned',
                    'status': 'ALREADY_SCANNED',
                    'attendance': AttendanceSerializer(existing_attendance).data
                }, status=status.HTTP_200_OK)
            
            # Create attendance record
            attendance = Attendance.objects.create(
                hall_ticket=hall_ticket,
                exam_id=exam_id,
                student=hall_ticket.student,
                status='PRESENT',
                scanned_by=request.user if request.user.is_authenticated else None,
                scanned_device=scanned_device
            )
            
            return Response({
                'success': True,
                'message': 'Attendance marked successfully',
                'status': 'VALID',
                'attendance': AttendanceSerializer(attendance).data,
                'student': StudentSerializer(hall_ticket.student).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def exam_report(self, request):
        """Get attendance report for an exam"""
        try:
            exam_id = request.query_params.get('exam_id')
            exam = get_object_or_404(Exam, id=exam_id)
            
            total_tickets = HallTicket.objects.filter(exam=exam, status='ACTIVE').count()
            marked_attendance = Attendance.objects.filter(exam=exam).count()
            
            attendance_data = Attendance.objects.filter(exam=exam).values(
                'status'
            ).annotate(count=Count('id'))
            
            return Response({
                'exam': ExamSerializer(exam).data,
                'total_tickets': total_tickets,
                'marked_attendance': marked_attendance,
                'attendance_breakdown': attendance_data
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==================== ADMIN USER VIEWSET ====================

class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]


# ==================== DASHBOARD VIEWS ====================

def login_page(request):
    """Login page - accessible without authentication"""
    return render(request, 'login.html')


def admin_dashboard(request):
    """Admin dashboard page - JWT auth handled client-side"""
    return render(request, 'admin/dashboard.html')


def student_portal(request):
    """Student portal page - JWT auth handled client-side"""
    return render(request, 'student/portal.html')


def staff_scanner(request):
    """Staff QR scanner page - JWT auth handled client-side"""
    return render(request, 'staff/scanner.html')
