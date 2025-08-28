from django.db import models
from classesApp.models import ClassRoom, Subjects

class Exam(models.Model):
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    exam_date = models.DateField()
    max_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.subject.subject} - {self.class_room.name} ({self.exam_date})"
