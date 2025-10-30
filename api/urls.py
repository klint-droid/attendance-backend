from rest_framework import routers
from .views import StudentViewSet, AttendanceViewSet, import_students_csv, export_attendance_csv, export_attendance_excel, export_attendance_pdf
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'students', StudentViewSet, basename='students')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
    path('students/import_csv/', import_students_csv, name='import-students-csv'),
    path('export-attendance/csv/', export_attendance_csv, name='export_attendance_csv'),
    path('export-attendance/excel/', export_attendance_excel, name='export_attendance_excel'),
    path('export-attendance/pdf/', export_attendance_pdf, name='export_attendance_pdf'),
]