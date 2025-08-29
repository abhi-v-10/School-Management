from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import *
from django.contrib import messages

from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from studentsApp.models import Student
from teachersApp.models import Teacher
from classesApp.models import ClassRoom
from attendanceApp.models import Attendance
from examsApp.models import Exam  # removed ExamResult
from messagingApp.models import Message
from parentsApp.models import Parent  # added for parent count
from accountsApp.models import Notice  # added for notifications
from django.urls import reverse

def home(request):
    return render(request, 'home.html')

def register_admin(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = AdminRegistrationForm()
    return render(request, 'accountsApp/register.html', {'form': form})

def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'accountsApp/register.html', {'form': form})

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = StudentRegistrationForm()
    return render(request, 'accountsApp/register.html', {'form': form})

def register_parent(request):
    if request.method == 'POST':
        form = ParentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = ParentRegistrationForm()
    return render(request, 'accountsApp/register.html', {'form': form})

def login_user(request):
    # Handle normal and AJAX login requests. For AJAX we return JSON so the client
    # can show the success animation and delay before performing the redirect.
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # on AJAX requests return JSON with redirect URL
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect_url': reverse('home')})
            return redirect('home')
        else:
            # invalid credentials
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': ['Invalid credentials.']}, status=400)
            messages.error(request, "Invalid credentials. Please try again.")
    return render(request, 'accountsApp/login.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard_admin(request):
    if request.user.role != 'admin':
        return render(request, 'errors/403.html')

    context = {
        "student_count": Student.objects.count(),
        "teacher_count": Teacher.objects.count(),
        "parent_count": Parent.objects.count(),
        "class_count": ClassRoom.objects.count(),
        "exam_count": Exam.objects.count(),
        "notification_count": Notice.objects.count(),
        "recent_attendance": Attendance.objects.order_by('-date')[:5],
        "recent_messages": Message.objects.order_by('-timestamp')[:5],
        "recent_exams": Exam.objects.order_by('-exam_date')[:5],
        "recent_students": Student.objects.order_by('-admission_date')[:5],
        "recent_notifications": Notice.objects.order_by('-created_at')[:5],
        "active_users": get_user_model().objects.filter(is_active=True).count(),
    }
    return render(request, "accountsApp/dashboard.html", context)

User = get_user_model()

@login_required
def profile_view(request):
    if request.method == 'POST':
        if 'remove_photo' in request.POST:
            if request.user.profile_photo:
                request.user.profile_photo.delete(save=False)
            request.user.profile_photo = None
            request.user.save()
            messages.success(request, "Profile photo removed.")
            return redirect('profile')
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accountsApp/profile.html', {'form': form})


@login_required
def notice_list(request):
    notices = Notice.objects.order_by('-created_at')
    return render(request, "accountsApp/notice_list.html", {"notices": notices})


@login_required
def notice_create(request):
    user = request.user
    if not user.role == 'admin':  # Only admin can create
        return redirect("notice_list")

    if request.method == "POST":
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.created_by = request.user
            notice.save()
            return redirect("notice_list")
    else:
        form = NoticeForm()

    return render(request, "accountsApp/notice_form.html", {"form": form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ChangePasswordForm

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('profile')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'accountsApp/change_password.html', {'form': form})
