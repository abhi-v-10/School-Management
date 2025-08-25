from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('register/admin/', views.register_admin, name='register_admin'),
    path('register/teacher/', views.register_teacher, name='register_teacher'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/parent/', views.register_parent, name='register_parent'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path("notices/", views.notice_list, name="notice_list"),
    path("notices/create/", views.notice_create, name="notice_create"),
]