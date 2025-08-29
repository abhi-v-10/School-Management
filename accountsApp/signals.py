from django.db.models.signals import post_save
from django.dispatch import receiver
from accountsApp.models import User
from teachersApp.models import Teacher
from studentsApp.models import Student
from parentsApp.models import Parent

@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'teacher':
            Teacher.objects.create(user=instance)
        elif instance.role == 'student':
            Student.objects.create(user=instance)
        elif instance.role == 'parent':
            Parent.objects.create(user=instance, phone_number='')