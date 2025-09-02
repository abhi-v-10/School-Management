from django.db import models
from accountsApp.models import User
from classesApp.models import ClassRoom, Subjects


def resource_upload_path(instance, filename):
    return f"resources/{instance.class_room.id}/{filename}" if instance.class_room_id else f"resources/uncategorized/{filename}"

class Resource(models.Model):
    RESOURCE_TYPES = (
        ("document", "Document"),
        ("presentation", "Presentation"),
        ("image", "Image"),
        ("other", "Other"),
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='resources')
    subject = models.ForeignKey(Subjects, on_delete=models.SET_NULL, null=True, blank=True, related_name='resources')
    file = models.FileField(upload_to=resource_upload_path)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='document')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_resources')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

