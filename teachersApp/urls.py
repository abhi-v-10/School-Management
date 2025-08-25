from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/teacher/', views.dashboard_teacher, name='dashboard_teacher'),
    path('admin/teachers/', views.AdminTeacherList.as_view(), name='admin_teachers_list'),
    path('admin/teachers/<int:pk>/', views.AdminTeacherDetail.as_view(), name='admin_teacher_detail'),
    path('admin/teachers/<int:pk>/edit/', views.AdminTeacherUpdate.as_view(), name='admin_teacher_edit'),
    path("class/<int:class_id>/", views.teacher_class_detail, name="teacher_class_detail"),

]
