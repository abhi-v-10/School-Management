from django.shortcuts import render
from studentsApp.models import Student
from accountsApp.models import Notice
from django.contrib.auth.decorators import login_required
from attendanceApp.models import Attendance
from django.utils.timezone import now

@login_required
def dashboard_parent(request):
    parent = request.user.parent  # OneToOne relation
    children = Student.objects.filter(parent=parent)
    notices = Notice.objects.order_by('-created_at')[:5]
    today = now().date()
    attendance_records = Attendance.objects.filter(student__in=children, date=today)
    attendance_map = {rec.student.id: rec.status for rec in attendance_records}
    # overall attendance percentage (average across children)
    total_present = 0
    total_marked = 0
    for child in children:
        child_att = Attendance.objects.filter(student=child)
        child_total = child_att.count()
        if child_total:
            child_present = child_att.filter(status='present').count()
            total_present += (child_present / child_total) * 100
            total_marked += 1
    avg_attendance_pct = round(total_present / total_marked, 1) if total_marked else 0
    stats = {
        'children': children.count(),
        'avg_attendance_pct': avg_attendance_pct,
        'notices': notices.count(),
    }
    context = {
        "parent": parent,
        "children": children,
        "notices": notices,
        "attendance_map": attendance_map,
        "stats": stats,
    }
    return render(request, "parentsApp/dashboard.html", context)
