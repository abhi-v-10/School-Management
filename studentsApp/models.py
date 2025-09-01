from django.db import models
from accountsApp.models import User
from classesApp.models import ClassRoom
from parentsApp.models import Parent


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    class_room = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    admission_date = models.DateField(auto_now_add=True)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True, blank=True, related_name='parent_contact')
    # Email a student provides at registration time to later auto-link a Parent
    parent_email = models.EmailField(null=True, blank=True, help_text="Parent's email for auto-linking if parent registers later")

    def __str__(self):
        return self.user.username