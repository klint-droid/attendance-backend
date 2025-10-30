from django.db import models

# Create your models here.
class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True, default='Unknown')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, default='unknown@example.com')
    course = models.CharField(max_length=100, default='Unknown')

    def __str__(self):
        return f"{self.student_id} {self.name} ({self.course})"
    
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Absent')

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"

