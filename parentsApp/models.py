from django.db import models
from accountsApp.models import User

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)


    def __str__(self):
        return self.user.username
