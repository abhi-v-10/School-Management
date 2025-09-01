from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import get_connection, EmailMessage
from django.utils import timezone
from accountsApp.models import User
from .models import Exam

@receiver(post_save, sender=Exam)
def send_exam_scheduled_emails(sender, instance, created, **kwargs):
    if not created:
        return
    # Gather all users with an email
    users = User.objects.exclude(email__isnull=True).exclude(email__exact='')
    if not users:
        return
    exam_date_str = instance.exam_date.strftime('%Y-%m-%d')
    subject_line = f"Exam Scheduled: {instance.subject.subject} on {exam_date_str}"

    body_core = (
        f"Subject: {instance.subject.subject}\n"
        f"Class: {instance.class_room.name} {instance.class_room.section}\n"
        f"Exam Date: {exam_date_str}\n"
        f"Maximum Marks: {instance.max_marks}\n"
        f"Scheduled At: {timezone.now().strftime('%Y-%m-%d')}\n"
    )

    connection = get_connection(fail_silently=True)
    emails = []
    for user in users:
        role = user.role
        if role == 'teacher':
            role_message = (
                "Please prepare your exam paper with proper, syllabus-aligned questions and submit it before the deadline."
            )
        elif role == 'student':
            role_message = (
                "This is a reminder to start (or keep) studying. Stay focused and give your best preparation!"
            )
        elif role == 'parent':
            role_message = (
                "We are notifying you that your child has an upcoming exam. Kindly support and encourage their preparation."
            )
        else:  # admin or any other
            role_message = "An exam has been scheduled."
        personalized = (
            f"Hello {user.first_name or user.username},\n\nA new exam has been scheduled.\n\n"
            f"{body_core}\n{role_message}\n\nRegards,\nAdministration"
        )
        emails.append(EmailMessage(subject=subject_line, body=personalized, to=[user.email]))
    connection.send_messages(emails)

