from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from accountsApp.models import  User, Notice
from django.utils.timezone import now
from attendanceApp.models import Attendance
from examsApp.models import Exam, ExamResult
from django.db.models import Q
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from accountsApp.mixins import AdminRequiredMixin
from .models import Student
from .forms import StudentAdminForm

class AdminStudentList(AdminRequiredMixin, ListView):
    model = Student
    template_name = 'studentsApp/admin_student_list.html'
    paginate_by = 12

    def get_queryset(self):
        qs = Student.objects.select_related('user', 'class_room', 'parent').all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__username__icontains=q) |
                Q(parent__phone_number__icontains=q) |  # fixed here
                Q(class_room__name__icontains=q) |
                Q(class_room__section__icontains=q) |
                Q(parent__user__first_name__icontains=q) |  # search by parent's name too
                Q(parent__user__last_name__icontains=q)
            )
        return qs.order_by('user__first_name')


class AdminStudentDetail(AdminRequiredMixin, DetailView):
    model = Student
    template_name = 'studentsApp/admin_student_detail.html'

class AdminStudentUpdate(AdminRequiredMixin, UpdateView):
    model = Student
    form_class = StudentAdminForm
    template_name = 'studentsApp/admin_student_form.html'

    def get_success_url(self):
        messages.success(self.request, "Student updated.")
        return reverse_lazy('admin_student_detail', kwargs={'pk': self.object.pk})


@login_required
def dashboard_student(request):
    student = Student.objects.get(user=request.user)
    exams = Exam.objects.filter(class_room=student.class_room)
    results = ExamResult.objects.filter(student=student)
    notices = Notice.objects.order_by('-created_at')[:5]
    today = now().date()
    today_record = Attendance.objects.filter(student=student, date=today).first()
    history = Attendance.objects.filter(student=student).order_by('-date')[:10]  # last 10

    context = {
        "student": student,
        "exams": exams,
        "results": results,
        "notices": notices,
        "today_record": today_record,
        "history": history,
    }
    return render(request, "studentsApp/dashboard.html", context )