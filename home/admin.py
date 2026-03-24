from django.contrib import admin
from .models import Student, Exam, HallTicket, Attendance, AdminUser, Subject, Room

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'name', 'batch', 'branch')
    search_fields = ('roll_number', 'name')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('subject_code', 'subject_name', 'date', 'room_number')
    search_fields = ('subject_code', 'subject_name')

@admin.register(HallTicket)
class HallTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'student', 'exam', 'status')
    list_filter = ('status', 'exam')
    search_fields = ('ticket_number', 'student__roll_number')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'status', 'scanned_at')
    list_filter = ('status', 'exam')

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'capacity', 'rows', 'cols')
