from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/parent/', views.dashboard_parent, name='dashboard_parent'),
    path('dashboard/parent/link-child/', views.link_child, name='link_child'),
]