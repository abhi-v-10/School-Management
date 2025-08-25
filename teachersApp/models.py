from django.db import models
from accountsApp.models import User
from classesApp.models import ClassRoom, Subjects


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    subject = models.ManyToManyField(Subjects, related_name='assigned_subjects')
    assigned_class = models.ManyToManyField(ClassRoom, related_name='assigned_teachers')
    hire_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username
