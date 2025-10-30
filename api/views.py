from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Student, Attendance
from .serializers import StudentSerializer, AttendanceSerializer
import csv
from django.http import HttpResponse
from io import TextIOWrapper, BytesIO
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# -----------------------------
# Student API
# -----------------------------
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


# -----------------------------
# Attendance API
# -----------------------------
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def create(self, request, *args, **kwargs):
        # Support both single and bulk attendance creation
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# -----------------------------
# Import Students from CSV
# -----------------------------
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def import_students_csv(request):
    file = request.FILES.get('file')
    if not file:
        return Response({"error": "No file uploaded"}, status=400)
    
    data_set = TextIOWrapper(file.file, encoding='utf-8')
    reader = csv.DictReader(data_set)

    students_created = 0
    for row in reader:

        student_id = row.get('student_id')
        name = row.get('name')
        email = row.get('email')
        course = row.get('course')

        if name: 
            student, created = Student.objects.get_or_create(
                name=name,
                defaults={'email': email, 'course': course}
            )
            if created:
                students_created += 1

    return Response({"message": f"{students_created} students imported successfully!"})

# -----------------------------
# Download
# -----------------------------

def export_attendance_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_records.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Name', 'Course', 'Date', 'Status'])

    records = Attendance.objects.select_related('student').all().order_by('-date')

    for record in records:
        writer.writerow([
            record.student.student_id,
            record.student.name,
            record.student.course,
            record.date,
            record.status
        ])
    
    return response

def export_attendance_excel(request):
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="attendance_records.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance Records"

    # Header row
    ws.append(['Student ID', 'Name', 'Course', 'Date', 'Status'])

    # Data rows
    records = Attendance.objects.select_related('student').all().order_by('-date')
    for record in records:
        ws.append([
            record.student.student_id,
            record.student.name,
            record.student.course,
            str(record.date),
            record.status
        ])

    wb.save(response)
    return response

def export_attendance_pdf(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    p.setTitle("Attendance Report")
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Attendance Report")

    y = 760
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Student ID")
    p.drawString(150, y, "Name")
    p.drawString(300, y, "Course")
    p.drawString(420, y, "Date")
    p.drawString(500, y, "Status")

    y -= 20
    p.setFont("Helvetica", 11)

    records = Attendance.objects.select_related('student').all().order_by('-date')

    for record in records:
        if y < 50:  # Create new page if needed
            p.showPage()
            y = 800

        p.drawString(50, y, record.student.student_id)
        p.drawString(150, y, record.student.name[:20])
        p.drawString(300, y, record.student.course[:15])
        p.drawString(420, y, str(record.date))
        p.drawString(500, y, record.status)
        y -= 18

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_records.pdf"'
    response.write(pdf)
    return response