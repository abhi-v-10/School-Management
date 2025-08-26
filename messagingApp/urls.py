from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("inbox/", views.inbox, name="inbox"),
    path("conversation/<int:user_id>/", views.conversation, name="conversation"),
]