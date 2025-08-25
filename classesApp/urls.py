from django.urls import path
from . import views

urlpatterns = [
    path('admin/classes/', views.AdminClassList.as_view(), name='admin_classes_list'),
    path('admin/classes/create/', views.AdminClassCreate.as_view(), name='admin_class_create'),
    path('admin/classes/<int:pk>/edit/', views.AdminClassUpdate.as_view(), name='admin_class_edit'),

    path('admin/subjects/', views.AdminSubjectList.as_view(), name='admin_subjects_list'),
    path('admin/subjects/create/', views.AdminSubjectCreate.as_view(), name='admin_subject_create'),
    path('admin/subjects/<int:pk>/edit/', views.AdminSubjectUpdate.as_view(), name='admin_subject_edit'),
    path('<int:class_id>/', views.class_detail, name='class_detail')
]
