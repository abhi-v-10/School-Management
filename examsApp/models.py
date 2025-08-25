from django.db import models
from studentsApp.models import Student
from classesApp.models import ClassRoom, Subjects

class Exam(models.Model):
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    exam_date = models.DateField()
    max_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.subject.subject} - {self.class_room.name} ({self.exam_date})"

class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    marks_obtained = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.marks_obtained}"
