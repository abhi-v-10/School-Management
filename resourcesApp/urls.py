from django.urls import path
from django.views.generic import RedirectView
from . import views

"""Patterns mounted at /resources/ in project urls.
Final public URLs:
 /resources/teacher/        -> teacher_resources
 /resources/student/        -> student_resources
 /resources/<pk>/           -> resource_detail

Legacy (incorrect) path that appeared: /resources/teacher/resources/ (redirected)
"""

urlpatterns = [
    # Correct endpoints
    path('teacher/', views.teacher_resource_list_create, name='teacher_resources'),
    path('student/', views.student_resource_list, name='student_resources'),
    path('<int:pk>/', views.resource_detail_rate, name='resource_detail'),
    # Legacy redundant nesting redirect
    path('teacher/resources/', RedirectView.as_view(pattern_name='teacher_resources', permanent=False)),
]
