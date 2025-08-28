from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from accountsApp.mixins import AdminRequiredMixin
from .models import Exam
from .forms import ExamForm

class AdminExamList(AdminRequiredMixin, ListView):
    model = Exam
    template_name = 'examsApp/admin_exam_list.html'
    paginate_by = 15
    ordering = ['exam_date']

class AdminExamCreate(AdminRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'examsApp/admin_exam_form.html'
    success_url = reverse_lazy('admin_exams_list')

    def form_valid(self, form):
        messages.success(self.request, "Exam created.")
        return super().form_valid(form)

class AdminExamUpdate(AdminRequiredMixin, UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = 'examsApp/admin_exam_form.html'
    success_url = reverse_lazy('admin_exams_list')

    def form_valid(self, form):
        messages.success(self.request, "Exam updated.")
        return super().form_valid(form)

class TeacherExamList(ListView):
    model = Exam
    template_name = 'examsApp/teacher_exam_list.html'
    paginate_by = 15
    ordering = ['exam_date']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # allow only teachers
        if not hasattr(request.user, 'teacher'):
            return redirect('dashboard_teacher') if request.user.role == 'teacher' else redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        teacher = self.request.user.teacher
        classes = teacher.assigned_class.all()
        return Exam.objects.filter(class_room__in=classes).select_related('subject', 'class_room').order_by('exam_date')
