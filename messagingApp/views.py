from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Message
from accountsApp.models import User  # adjust import
from studentsApp.models import Student

@login_required
def inbox(request):
    conversations = Message.get_conversations(request.user)
    return render(request, "messagingApp/inbox.html", {"conversations": conversations})

@login_required
def conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # ---- Role-based restrictions ----
    if request.user.role == "admin":
        # Admin → Teacher or Parent
        if other_user.role not in ["teacher", "parent"]:
            return redirect("inbox")

    elif request.user.role == "teacher":
        # Teacher → Parent or Admin
        if other_user.role not in ["parent", "admin"]:
            return redirect("inbox")

    elif request.user.role == "parent":
        # Parent → Teacher only
        if other_user.role not in ["teacher", "admin"]:
            return redirect("inbox")

    else:
        # Students & any other roles not allowed
        return redirect("inbox")

    # ---- Fetch conversation messages ----
    chat_messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by("timestamp")

    # ---- Handle sending new message ----
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content.strip()
            )
        return redirect("conversation", user_id=other_user.id)

    return render(request, "messagingApp/conversation.html", {
        "other_user": other_user,
        "chat_messages": chat_messages,
    })
