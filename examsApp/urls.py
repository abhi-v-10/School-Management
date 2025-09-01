from django.urls import path
from . import views

urlpatterns = [
    path('admin/exams/', views.AdminExamList.as_view(), name='admin_exams_list'),
    path('admin/exams/create/', views.AdminExamCreate.as_view(), name='admin_exam_create'),
    path('admin/exams/<int:pk>/edit/', views.AdminExamUpdate.as_view(), name='admin_exam_edit'),
    path('admin/exams/<int:pk>/delete/', views.AdminExamDelete.as_view(), name='admin_exam_delete'),
    path('teacher/exams/', views.TeacherExamList.as_view(), name='teacher_exams_list'),
]
