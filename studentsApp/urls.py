from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/student/', views.dashboard_student, name='dashboard_student'),
    path('admin/studentsApp/', views.AdminStudentList.as_view(), name='admin_students_list'),
    path('admin/studentsApp/<int:pk>/', views.AdminStudentDetail.as_view(), name='admin_student_detail'),
    path('admin/studentsApp/<int:pk>/edit/', views.AdminStudentUpdate.as_view(), name='admin_student_edit'),
]