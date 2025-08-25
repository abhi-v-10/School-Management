from django.urls import path
from . import views

urlpatterns = [
    path('mark_attendance', views.mark_attendance, name='mark_attendance'),
    path("student/<int:student_id>/history/", views.student_attendance_history, name="student_attendance_history"),
    path("attendance_list", views.admin_attendance_list, name="admin_attendance_list"),

]