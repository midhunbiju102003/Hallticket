from django.urls import path, include
from rest_framework.routers import DefaultRouter
from home import views

router = DefaultRouter()
router.register(r'students', views.StudentViewSet, basename='student')
router.register(r'exams', views.ExamViewSet, basename='exam')
router.register(r'hall-tickets', views.HallTicketViewSet, basename='hallticket')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')
router.register(r'admin-users', views.AdminUserViewSet, basename='adminuser')
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'rooms', views.RoomViewSet, basename='room')

urlpatterns = [
    # Login page
    path('', views.login_page, name='login_page'),
    
    # API auth
    path('api/login/', views.login_view, name='login'),
    path('api/student-login/', views.student_login_view, name='student_login'),
    path('api/status/', views.api_status, name='api_status'),
    
    # API routes
    path('api/', include(router.urls)),
    
    # Web pages
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student/portal/', views.student_portal, name='student_portal'),
    path('staff/scanner/', views.staff_scanner, name='staff_scanner'),
]
