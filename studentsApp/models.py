from django.db import models
from accountsApp.models import User
from classesApp.models import ClassRoom
from parentsApp.models import Parent


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    class_room = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    admission_date = models.DateField(auto_now_add=True)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True, blank=True, related_name='parent_contact')

    def __str__(self):
        return self.user.get_full_name()