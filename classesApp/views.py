from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Count
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from studentsApp.models import Student
from attendanceApp.models import Attendance
from accountsApp.mixins import AdminRequiredMixin
from django.utils.timezone import now
from .models import ClassRoom, Subjects
from .forms import ClassRoomForm, SubjectForm

class AdminClassList(AdminRequiredMixin, ListView):
    model = ClassRoom
    template_name = 'classesApp/admin_class_list.html'
    paginate_by = 12

    def get_queryset(self):
        return ClassRoom.objects.annotate(num_students=Count('students')).order_by('name', 'section')
        # if your Student FK uses related_name='students'

class AdminClassCreate(AdminRequiredMixin, CreateView):
    model = ClassRoom
    form_class = ClassRoomForm
    template_name = 'classesApp/admin_class_form.html'
    success_url = reverse_lazy('admin_classes_list')

    def form_valid(self, form):
        messages.success(self.request, "Class created.")
        return super().form_valid(form)

class AdminClassUpdate(AdminRequiredMixin, UpdateView):
    model = ClassRoom
    form_class = ClassRoomForm
    template_name = 'classesApp/admin_class_form.html'
    success_url = reverse_lazy('admin_classes_list')

    def form_valid(self, form):
        messages.success(self.request, "Class updated.")
        return super().form_valid(form)

class AdminSubjectList(AdminRequiredMixin, ListView):
    model = Subjects
    template_name = 'classesApp/admin_subject_list.html'
    paginate_by = 15
    ordering = ['subject']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from teachersApp.models import Teacher
        subject_teacher_map = {}
        for subject in context['object_list']:
            teachers = Teacher.objects.filter(subject=subject)
            subject_teacher_map[subject.id] = teachers
        context['subject_teacher_map'] = subject_teacher_map
        return context

class AdminSubjectCreate(AdminRequiredMixin, CreateView):
    model = Subjects
    form_class = SubjectForm
    template_name = 'classesApp/admin_subject_form.html'
    success_url = reverse_lazy('admin_subjects_list')

    def form_valid(self, form):
        messages.success(self.request, "Subject created.")
        return super().form_valid(form)

class AdminSubjectUpdate(AdminRequiredMixin, UpdateView):
    model = Subjects
    form_class = SubjectForm
    template_name = 'classesApp/admin_subject_form.html'
    success_url = reverse_lazy('admin_subjects_list')

    def form_valid(self, form):
        messages.success(self.request, "Subject updated.")
        return super().form_valid(form)


def class_detail(request, class_id):
    classroom = get_object_or_404(ClassRoom, id=class_id)
    students = Student.objects.filter(class_room=classroom)

    # Get attendance for today
    today = now().date()
    attendance_records = Attendance.objects.filter(
        student__class_room=classroom,
        date=today
    )
    attendance_map = {record.student.id: record.status for record in attendance_records}

    return render(request, "classesApp/admin_class_detail.html", {
        "classroom": classroom,
        "students": students,
        "attendance_map": attendance_map,
        "today": today,
    })