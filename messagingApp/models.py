from django.db import models
from accountsApp.models import User

class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ("timestamp",)  # chronological order

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:30]}"

    @staticmethod
    def get_conversations(user):
        """Return distinct users this person has chatted with"""
        sent = Message.objects.filter(sender=user).values_list("receiver", flat=True)
        received = Message.objects.filter(receiver=user).values_list("sender", flat=True)
        user_ids = set(list(sent) + list(received))
        return User.objects.filter(id__in=user_ids)
