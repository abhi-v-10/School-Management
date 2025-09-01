from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from accountsApp.models import User
from classesApp.models import ClassRoom
from parentsApp.models import Parent
from teachersApp.models import Teacher

class Message(models.Model):
    """Direct 1:1 message (supports attachments, scheduling & reactions)."""

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField(blank=True)
    file = models.FileField(upload_to="messages/files/", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(null=True, blank=True, help_text="If set & in future, only visible to sender until due.")
    is_read = models.BooleanField(default=False)
    reactions = GenericRelation('Reaction', related_query_name='direct_message')

    class Meta:
        ordering = ("timestamp",)
        indexes = [
            models.Index(fields=["sender", "receiver", "timestamp"]),
            models.Index(fields=["scheduled_for"]),
        ]

    def __str__(self):
        base = self.content[:30] if self.content else (self.file.name if self.file else "<empty>")
        return f"{self.sender} → {self.receiver}: {base}"

    @property
    def is_visible(self):
        return (self.scheduled_for is None) or (self.scheduled_for <= timezone.now())

    @staticmethod
    def get_conversations(user):
        sent = Message.objects.filter(sender=user).values_list("receiver", flat=True)
        received = Message.objects.filter(receiver=user).values_list("sender", flat=True)
        user_ids = set(list(sent) + list(received))
        return User.objects.filter(id__in=user_ids)


class GroupChat(models.Model):
    """A chat group typically linked to a class/section (ClassRoom)."""
    name = models.CharField(max_length=150)
    class_room = models.OneToOneField(ClassRoom, on_delete=models.CASCADE, related_name="group_chat", null=True, blank=True,
                                      help_text="If set, this group auto-manages members (teachers + parents of students).")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_groups")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=["name"], name="uq_groupchat_name")
        ]

    def __str__(self):
        return self.name

    def sync_members_from_class(self):
        if not self.class_room:
            return
        # Add teachers assigned to this class
        teacher_users = User.objects.filter(teacher__assigned_class=self.class_room).distinct()
        parent_users = User.objects.filter(parent__parent_contact__class_room=self.class_room).distinct()
        # Add parents of students in this class (student.parent.user)
        student_parent_users = User.objects.filter(parent__parent_contact__class_room=self.class_room).distinct()
        all_users = set(list(teacher_users) + list(parent_users) + list(student_parent_users))
        for u in all_users:
            GroupMembership.objects.get_or_create(group=self, user=u)


class GroupMembership(models.Model):
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_memberships")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("group", "user")

    def __str__(self):
        return f"{self.user} in {self.group}"


class GroupMessage(models.Model):
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_messages_sent")
    content = models.TextField(blank=True)
    file = models.FileField(upload_to="messages/group_files/", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    reactions = GenericRelation('Reaction', related_query_name='group_message')

    class Meta:
        ordering = ("timestamp",)
        indexes = [
            models.Index(fields=["group", "timestamp"]),
            models.Index(fields=["scheduled_for"]),
        ]

    def __str__(self):
        return f"[{self.group}] {self.sender}: {self.content[:30]}"

    @property
    def is_visible(self):
        return (self.scheduled_for is None) or (self.scheduled_for <= timezone.now())


class GroupMessageRead(models.Model):
    message = models.ForeignKey(GroupMessage, on_delete=models.CASCADE, related_name="reads")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_reads")
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message", "user")


REACTION_CHOICES = [
    ("👍", "Thumbs Up"),
    ("❤️", "Heart"),
    ("😂", "Laugh"),
    ("😮", "Wow"),
    ("😢", "Sad"),
]


class Reaction(models.Model):
    """Emoji reaction for direct or group message (generic)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reactions")
    emoji = models.CharField(max_length=5, choices=REACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "emoji", "content_type", "object_id")
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.user} {self.emoji} {self.content_object}"

