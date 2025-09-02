from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Resource
from .forms import ResourceForm
from teachersApp.models import Teacher
from studentsApp.models import Student

@login_required
def teacher_resource_list_create(request):
    # Only teachers
    if not hasattr(request.user, 'teacher'):
        return HttpResponseForbidden()
    teacher = request.user.teacher
    resources = Resource.objects.filter(uploaded_by=request.user).select_related('class_room','subject')
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, teacher=teacher)
        if form.is_valid():
            res = form.save(commit=False)
            res.uploaded_by = request.user
            res.save()
            messages.success(request, 'Resource uploaded.')
            return redirect('teacher_resources')
    else:
        form = ResourceForm(teacher=teacher)
    return render(request, 'resourcesApp/teacher_resources.html', {
        'form': form,
        'resources': resources,
    })

@login_required
def student_resource_list(request):
    if not hasattr(request.user, 'student'):
        return HttpResponseForbidden()
    student = request.user.student
    # Show resources for student's class
    resources = Resource.objects.filter(class_room=student.class_room).select_related('uploaded_by','subject').order_by('-created_at')
    return render(request, 'resourcesApp/student_resources.html', {
        'resources': resources,
    })

@login_required
def resource_detail_rate(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    # Students can view if same class. Teachers can view their own.
    if hasattr(request.user, 'student'):
        if resource.class_room_id != request.user.student.class_room_id:
            return HttpResponseForbidden()
    elif hasattr(request.user, 'teacher'):
        if resource.uploaded_by_id != request.user.id:
            # allow teacher if teaching that class
            if resource.class_room not in request.user.teacher.assigned_class.all():
                return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()

    return render(request, 'resourcesApp/resource_detail.html', {
        'resource': resource,
    })
