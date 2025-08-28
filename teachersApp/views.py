from django.db.models import Q
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from accountsApp.mixins import AdminRequiredMixin
from .forms import TeacherAdminForm
from classesApp.models import ClassRoom, Subjects
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from studentsApp.models import Student
from attendanceApp.models import Attendance
from examsApp.models import Exam
from .models import Teacher
from accountsApp.models import Notice

class AdminTeacherList(AdminRequiredMixin, ListView):
    model = Teacher
    template_name = 'teachersApp/admin_teacher_list.html'
    paginate_by = 12

    def get_queryset(self):
        qs = Teacher.objects.select_related('user').prefetch_related('subject', 'assigned_class')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__username__icontains=q) |
                Q(subject__name__icontains=q) |
                Q(assigned_class__name__icontains=q) |
                Q(assigned_class__section__icontains=q)
            ).distinct()
        return qs.order_by('user__first_name')

class AdminTeacherDetail(AdminRequiredMixin, DetailView):
    model = Teacher
    template_name = 'teachersApp/admin_teacher_detail.html'

    def get_queryset(self):
        return Teacher.objects.select_related('user').prefetch_related('subject', 'assigned_class')


class AdminTeacherUpdate(AdminRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherAdminForm
    template_name = 'teachersApp/admin_teacher_edit.html'

    def get_success_url(self):
        messages.success(self.request, "Teacher updated.")
        return reverse_lazy('admin_teacher_detail', kwargs={'pk': self.object.pk})


@login_required
def dashboard_teacher(request):
    teacher = Teacher.objects.get(user=request.user)
    classes = teacher.assigned_class.all()
    subjects = teacher.subject.all()
    exams = Exam.objects.filter(class_room__in=classes).order_by('exam_date')
    notices = Notice.objects.order_by('-created_at')[:5]
    total_students = Student.objects.filter(class_room__in=classes).distinct().count()
    context = {
        "teacher": teacher,
        "classes": classes,
        "subjects": subjects,
        "exams": exams[:6],
        "exams_full": exams,
        "notices": notices,
        "stats": {
            "classes": classes.count(),
            "subjects": subjects.count(),
            "students": total_students,
            "upcoming_exams": exams.count(),
        }
    }
    return render(request, "teachersApp/dashboard.html", context)

@login_required
def teacher_class_detail(request, class_id):
    classroom = get_object_or_404(ClassRoom, id=class_id)
    teacher = request.user.teacher

    # Only allow if this class is assigned to the teacher
    if classroom not in teacher.assigned_class.all():
        return redirect("dashboard_teacher")

    students = Student.objects.filter(class_room=classroom)
    today = now().date()

    if request.method == "POST":
        for student in students:
            status = request.POST.get(f"status_{student.id}")
            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=today,
                    defaults={"status": status, "teacher": teacher}
                )
        return redirect("teacher_class_detail", class_id=classroom.id)

    # Load today's attendance if already marked
    attendance_records = Attendance.objects.filter(
        student__in=students,
        date=today
    )
    attendance_map = {record.student.id: record.status for record in attendance_records}

    return render(request, "teachersApp/class_detail.html", {
        "classroom": classroom,
        "students": students,
        "attendance_map": attendance_map,
        "today": today,
    })