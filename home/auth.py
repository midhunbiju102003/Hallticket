from rest_framework.authentication import SessionAuthentication, BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
import jwt
from django.conf import settings
from home.models import Student

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        try:
            # Expected format: "Bearer <token>"
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return None
            
            token = parts[1]
            payload = jwt.decode(token, 'hall_ticket_secret', algorithms=['HS256'])
            
            # Handle both Admin/Staff (user_id) and Student (student_id)
            if 'user_id' in payload:
                user = User.objects.filter(id=payload['user_id']).first()
                if not user:
                    raise AuthenticationFailed('User not found')
                return (user, None)
            
            elif 'student_id' in payload:
                # For students, we might need a dummy user or handle it specifically
                # Since Student model doesn't inherit from User, we return the student record
                # and handle 'IsAuthenticated' checks accordingly.
                # However, DRF's IsAuthenticated expects a User object.
                # Let's map it to a student user if possible or just handle student auth.
                try:
                    student = Student.objects.get(id=payload['student_id'])
                    # Create or get a dummy student user to satisfy IsAuthenticated
                    user, created = User.objects.get_or_create(
                        username=f"student_{student.roll_number}",
                        defaults={'first_name': student.name}
                    )
                    return (user, None)
                except Student.DoesNotExist:
                    raise AuthenticationFailed('Student not found')
            
            return None
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            raise AuthenticationFailed(str(e))

