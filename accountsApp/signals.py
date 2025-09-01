from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import get_connection, EmailMessage
from accountsApp.models import User, Notice
from teachersApp.models import Teacher
from parentsApp.models import Parent
from studentsApp.models import Student

@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'teacher':
            Teacher.objects.create(user=instance)
        elif instance.role == 'student':
            Student.objects.create(user=instance, parent_email='')
        elif instance.role == 'parent':
            parent_obj = Parent.objects.create(user=instance, phone_number='')
            # auto-link any existing students that specified this email
            # (removed inner import to avoid UnboundLocalError)
            if instance.email:
                matches = Student.objects.filter(parent__isnull=True, parent_email__iexact=instance.email)
                for stu in matches:
                    stu.parent = parent_obj
                    stu.save(update_fields=['parent'])

@receiver(post_save, sender=Notice)
def send_notice_email(sender, instance, created, **kwargs):
    if not created:
        return
    users = User.objects.exclude(email__isnull=True).exclude(email__exact='')
    if not users:
        return
    subject = f"Notice: {instance.title}".strip()
    body_template = f"A new notice has been posted.\n\nTitle: {instance.title}\nMessage:\n{instance.message}\n\nPosted on: {instance.created_at.strftime('%Y-%m-%d %H:%M')}"
    connection = get_connection(fail_silently=True)
    emails = []
    for user in users:
        personalized = f"Hello {user.first_name or user.username},\n\n{body_template}\n\nRegards,\nAdministration"
        emails.append(EmailMessage(subject=subject, body=personalized, to=[user.email]))
    connection.send_messages(emails)
