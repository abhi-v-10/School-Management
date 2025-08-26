from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/students/', views.dashboard_student, name='dashboard_student'),
    path('admin/students/', views.AdminStudentList.as_view(), name='admin_students_list'),
    path('admin/students/<int:pk>/', views.AdminStudentDetail.as_view(), name='admin_student_detail'),
    path('admin/students/<int:pk>/edit/', views.AdminStudentUpdate.as_view(), name='admin_student_edit'),
]