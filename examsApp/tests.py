from django.test import TestCase
from django.core import mail
from django.urls import reverse
from datetime import date
from accountsApp.models import User
from classesApp.models import ClassRoom, Subjects
from examsApp.models import Exam

class TestExamEmailSignal(TestCase):
    def setUp(self):
        # Users
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin', email='admin@example.com')
        self.teacher = User.objects.create_user(username='teacher', password='pass', role='teacher', email='teacher@example.com')
        self.parent = User.objects.create_user(username='parent', password='pass', role='parent', email='parent@example.com')
        self.student = User.objects.create_user(username='student', password='pass', role='student', email='student@example.com')
        # Supporting models
        self.class_room = ClassRoom.objects.create(name='Grade 5', section='A', capacity=30)
        self.subject = Subjects.objects.create(subject='Mathematics')

    def test_exam_creation_sends_role_based_emails(self):
        Exam.objects.create(class_room=self.class_room, subject=self.subject, exam_date=date(2025, 9, 1), max_marks=100)
        self.assertEqual(len(mail.outbox), 4)
        for m in mail.outbox:
            self.assertIn('Exam Scheduled: Mathematics on 2025-09-01', m.subject)
        teacher_body = next(m.body for m in mail.outbox if 'teacher@example.com' in m.to)
        self.assertIn('syllabus-aligned questions', teacher_body)
        student_body = next(m.body for m in mail.outbox if 'student@example.com' in m.to)
        self.assertIn('Stay focused and give your best preparation!', student_body)
        parent_body = next(m.body for m in mail.outbox if 'parent@example.com' in m.to)
        self.assertIn('upcoming exam. Kindly support and encourage', parent_body)
        admin_body = next(m.body for m in mail.outbox if 'admin@example.com' in m.to)
        self.assertIn('A new exam has been scheduled.', admin_body)

    def test_exam_update_does_not_resend(self):
        exam = Exam.objects.create(class_room=self.class_room, subject=self.subject, exam_date=date(2025, 9, 1), max_marks=100)
        self.assertEqual(len(mail.outbox), 4)
        mail.outbox.clear()
        exam.max_marks = 120
        exam.save()
        self.assertEqual(len(mail.outbox), 0)

class TestExamDeletion(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin', email='admin@example.com')
        self.teacher = User.objects.create_user(username='teacher', password='pass', role='teacher', email='teacher@example.com')
        self.class_room = ClassRoom.objects.create(name='Grade 6', section='B', capacity=35)
        self.subject = Subjects.objects.create(subject='Science')
        self.exam = Exam.objects.create(class_room=self.class_room, subject=self.subject, exam_date=date(2025, 10, 1), max_marks=80)

    def test_admin_can_delete_exam(self):
        self.client.login(username='admin', password='pass')
        url = reverse('admin_exam_delete', args=[self.exam.pk])
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)
        resp_post = self.client.post(url)
        self.assertRedirects(resp_post, reverse('admin_exams_list'))
        self.assertFalse(Exam.objects.filter(pk=self.exam.pk).exists())

    def test_non_admin_cannot_delete_exam(self):
        self.client.login(username='teacher', password='pass')
        url = reverse('admin_exam_delete', args=[self.exam.pk])
        resp = self.client.get(url)
        # Should redirect due to permission denial
        self.assertNotEqual(resp.status_code, 200)
        self.assertTrue(Exam.objects.filter(pk=self.exam.pk).exists())
