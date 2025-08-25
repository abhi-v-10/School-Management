# messagingApp/views.py
from django.shortcuts import render, redirect
from .models import Message
from accountsApp.models import User
from django.contrib.auth.decorators import login_required

@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user)
    return render(request, "messagingApp/inbox.html", {"messages": messages})

@login_required
def send_message(request):
    users = User.objects.exclude(id=request.user.id)  # all except self
    if request.method == "POST":
        receiver_id = request.POST.get("receiver")
        content = request.POST.get("content")
        Message.objects.create(sender=request.user, receiver_id=receiver_id, content=content)
        return redirect("inbox")
    return render(request, "messagingApp/send_message.html", {"users": users})
