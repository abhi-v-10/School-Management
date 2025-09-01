from django.test import TestCase
from django.core import mail
from django.utils import timezone
from accountsApp.models import User, Notice

class NoticeEmailSignalTests(TestCase):
    def setUp(self):
        # Create users of each role with emails
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin', email='admin@example.com')
        self.teacher = User.objects.create_user(username='teacher', password='pass', role='teacher', email='teacher@example.com')
        self.parent = User.objects.create_user(username='parent', password='pass', role='parent', email='parent@example.com')
        self.student = User.objects.create_user(username='student', password='pass', role='student', email='student@example.com')

    def test_notice_creation_sends_emails(self):
        Notice.objects.create(title='Holiday', message='School will remain closed tomorrow', created_by=self.admin)
        self.assertEqual(len(mail.outbox), 4)
        subjects = {m.subject for m in mail.outbox}
        self.assertIn('Notice: Holiday', subjects)

    def test_notice_update_does_not_resend(self):
        n = Notice.objects.create(title='Event', message='Annual day', created_by=self.admin)
        self.assertEqual(len(mail.outbox), 4)
        mail.outbox.clear()
        n.message = 'Annual day updated details'
        n.save()  # should not trigger new emails
        self.assertEqual(len(mail.outbox), 0)
