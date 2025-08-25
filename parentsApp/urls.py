from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/parent/', views.dashboard_parent, name='dashboard_parent'),
]