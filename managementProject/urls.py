"""
URL configuration for managementProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from accountsApp.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('social_django.urls', namespace='social')),

    path('', home, name='home'),
    path('accounts/', include('accountsApp.urls')),
    path('students/', include('studentsApp.urls')),
    path('teachers/', include('teachersApp.urls')),
    path('parents/', include('parentsApp.urls')),
    path('classes/', include('classesApp.urls')),
    path('exams/', include('examsApp.urls')),
    # path('messages/', include('messagingApp.urls')),
    path('attendance/', include('attendanceApp.urls')),
]
