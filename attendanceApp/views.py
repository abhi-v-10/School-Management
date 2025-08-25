# attendanceApp/views.py
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Attendance
from studentsApp.models import Student
from classesApp.models import ClassRoom
from django.utils.timezone import now

def mark_attendance(request, class_id):
    classroom = ClassRoom.objects.get(id=class_id)
    students = Student.objects.filter(class_room=classroom)

    if request.method == "POST":
        for student in students:
            status = request.POST.get(f"status_{student.id}")
            Attendance.objects.update_or_create(
                student=student,
                date=now().date(),
                defaults={"status": status, "class_room": classroom},
            )
        return redirect("dashboard_teacher")

    return render(request, "attendanceApp/mark_attendance.html", {
        "classroom": classroom,
        "students": students,
    })

@login_required
def student_attendance_history(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    records = Attendance.objects.filter(student=student).order_by("-date")
    return render(request, "attendanceApp/student_history.html", {
        "student": student,
        "records": records
    })

@staff_member_required
def admin_attendance_list(request):
    # Get all attendance records, newest first
    records = Attendance.objects.select_related(
        "student__user", "student__class_room", "teacher__user"
    ).order_by("-date")

    return render(request, "attendanceApp/admin_attendance_list.html", {
        "records": records
    })