from django.shortcuts import render
from studentsApp.models import Student
from examsApp.models import ExamResult
from accountsApp.models import Notice
from django.contrib.auth.decorators import login_required
from attendanceApp.models import Attendance
from django.utils.timezone import now

@login_required
def dashboard_parent(request):
    parent = request.user.parent  # OneToOne relation
    children = Student.objects.filter(parent=parent)
    notices = Notice.objects.order_by('-created_at')[:5]
    # Fetch results for all children
    results = ExamResult.objects.filter(student__in=children).select_related('exam', 'student')
    today = now().date()
    attendance_records = Attendance.objects.filter(
        student__in=children,
        date=today
    )
    attendance_map = {rec.student.id: rec.status for rec in attendance_records}

    context = {
        "parent": parent,
        "children": children,
        "results": results,
        "notices": notices,
        "attendance_map": attendance_map

    }
    return render(request, "parentsApp/dashboard.html", context)
