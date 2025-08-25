from django.db import models

class ClassRoom(models.Model):
    name = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField(default=25)

    def __str__(self):
        return f"{self.name} - {self.section}"

class Subjects(models.Model):
    subject = models.CharField(max_length=50)

    def __str__(self):
        return self.subject

