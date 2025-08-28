from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, Subquery, OuterRef
from .models import Message
from accountsApp.models import User  # adjust import
from studentsApp.models import Student

@login_required
def inbox(request):
    conversations_qs = Message.get_conversations(request.user)
    user_ids = list(conversations_qs.values_list('id', flat=True))

    annotated_conversations = []
    if user_ids:
        # Subquery for latest message (timestamp + content) per partner
        msgs_between = Message.objects.filter(
            Q(sender=request.user, receiver=OuterRef('pk')) | Q(sender=OuterRef('pk'), receiver=request.user)
        ).order_by('-timestamp')

        annotated_conversations = (
            conversations_qs
            .annotate(
                latest_timestamp=Subquery(msgs_between.values('timestamp')[:1]),
                latest_content=Subquery(msgs_between.values('content')[:1]),
                unread_count=Count('sent_messages', filter=Q(sent_messages__receiver=request.user, sent_messages__is_read=False))
            )
            .order_by('-latest_timestamp')
        )

    role = getattr(request.user, "role", None)
    if role == "student":
        dashboard_url_name = "dashboard_student"
    elif role == "teacher":
        dashboard_url_name = "dashboard_teacher"
    elif role == "parent":
        dashboard_url_name = "dashboard_parent"
    elif role == "admin":
        dashboard_url_name = "dashboard_admin"
    else:
        dashboard_url_name = "home"
    return render(request, "messagingApp/inbox.html", {
        "conversations": annotated_conversations,
        "dashboard_url_name": dashboard_url_name,
    })

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

    # Mark unread incoming messages as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    # ---- Handle sending new message ----
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content
            )
        return redirect("conversation", user_id=other_user.id)

    return render(request, "messagingApp/conversation.html", {
        "other_user": other_user,
        "chat_messages": chat_messages,
    })
