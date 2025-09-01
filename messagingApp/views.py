from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count, Subquery, OuterRef
from django.utils import timezone
import time
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import (
    Message,
    GroupChat,
    GroupMessage,
    GroupMembership,
    GroupMessageRead,
    Reaction,
)
from accountsApp.models import User  # adjust import
from classesApp.models import ClassRoom

# ------------ Helper utilities -------------
def _user_dashboard_url_name(user):
    role = getattr(user, "role", None)
    return {
        "student": "dashboard_student",
        "teacher": "dashboard_teacher",
        "parent": "dashboard_parent",
        "admin": "dashboard_admin",
    }.get(role, "home")

@login_required
def inbox(request):
    # --- Conversations (direct) ---
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

    # --- Groups ---
    memberships = GroupMembership.objects.filter(user=request.user).select_related("group")
    groups = [m.group for m in memberships]

    # --- Inline search (optional) ---
    term = request.GET.get("q", "").strip()
    search_results = []
    if term:
        # Direct messages
        direct_msgs = Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user),
            content__icontains=term
        ).order_by('-timestamp')[:50]
        now = timezone.now()
        direct_msgs = [m for m in direct_msgs if m.is_visible]
        # Group messages
        group_ids = [g.id for g in groups]
        group_msgs = GroupMessage.objects.filter(group_id__in=group_ids, content__icontains=term).order_by('-timestamp')[:50]
        group_msgs = [gm for gm in group_msgs if gm.is_visible]
        # Normalize for template: list of dicts
        for m in direct_msgs:
            other = m.receiver if m.sender == request.user else m.sender
            search_results.append({
                'type': 'direct',
                'other': other,
                'sender': m.sender,
                'content': m.content,
                'timestamp': m.timestamp,
                'file': m.file,
            })
        for gm in group_msgs:
            search_results.append({
                'type': 'group',
                'group': gm.group,
                'sender': gm.sender,
                'content': gm.content,
                'timestamp': gm.timestamp,
                'file': gm.file,
            })
        # Sort combined by timestamp desc
        search_results.sort(key=lambda x: x['timestamp'], reverse=True)

    dashboard_url_name = _user_dashboard_url_name(request.user)
    return render(request, "messagingApp/inbox.html", {
        "conversations": annotated_conversations,
        "groups": groups,
        "search_term": term,
        "search_results": search_results,
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
    chat_messages_qs = (Message.objects
        .filter(Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user))
        .select_related('sender', 'receiver')
        .prefetch_related('reactions')
        .order_by('timestamp'))

    # Mark unread incoming messages as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    # ---- Handle sending new message ----
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        uploaded_file = request.FILES.get('file')
        if content or uploaded_file:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content,
                file=uploaded_file
            )
        return redirect("conversation", user_id=other_user.id)

    visible_messages = [m for m in chat_messages_qs if m.is_visible]
    # Keep only latest N messages to avoid long history clutter
    MAX_INITIAL = 50
    if len(visible_messages) > MAX_INITIAL:
        visible_messages = visible_messages[-MAX_INITIAL:]
    return render(request, "messagingApp/conversation.html", {
        "other_user": other_user,
        "chat_messages": visible_messages,
    })


# ------------- Group Messaging ---------------
@login_required
def groups(request):
    """List groups the user belongs to."""
    memberships = GroupMembership.objects.filter(user=request.user).select_related("group")
    dashboard_url_name = _user_dashboard_url_name(request.user)
    return render(request, "messagingApp/groups.html", {
        "memberships": memberships,
        "dashboard_url_name": dashboard_url_name,
    })


@login_required
def create_group(request):
    """Teachers can create section groups for their assigned classes; Admin can create any group."""
    if request.user.role not in ["teacher", "admin"]:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        class_room_id = request.POST.get("class_room")
        class_room = None
        if class_room_id:
            class_room = get_object_or_404(ClassRoom, id=class_room_id)
            # Validate teacher has that class
            if request.user.role == "teacher" and request.user.teacher.assigned_class.filter(id=class_room.id).count() == 0:
                return HttpResponseForbidden("Cannot create group for class you are not assigned")
        if name:
            group = GroupChat.objects.create(name=name, class_room=class_room, created_by=request.user)
            GroupMembership.objects.create(group=group, user=request.user)
            if class_room:
                group.sync_members_from_class()
            return redirect("group_chat", group_id=group.id)

    # Provide teacher's classes for selection
    teacher_classes = []
    if request.user.role == "teacher":
        teacher_classes = request.user.teacher.assigned_class.all()
    elif request.user.role == "admin":
        teacher_classes = ClassRoom.objects.all()
    dashboard_url_name = _user_dashboard_url_name(request.user)
    return render(request, "messagingApp/create_group.html", {
        "classes": teacher_classes,
        "dashboard_url_name": dashboard_url_name,
    })


@login_required
def group_chat(request, group_id):
    group = get_object_or_404(GroupChat, id=group_id)
    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        return HttpResponseForbidden("Not a member")

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        scheduled_for_str = request.POST.get("scheduled_for")
        uploaded_file = request.FILES.get("file")
        scheduled_for = None
        if scheduled_for_str:
            try:
                scheduled_for = timezone.datetime.fromisoformat(scheduled_for_str)
                if scheduled_for.tzinfo is None:
                    scheduled_for = timezone.make_aware(scheduled_for)
            except Exception:
                scheduled_for = None
        if content or uploaded_file:
            GroupMessage.objects.create(
                group=group,
                sender=request.user,
                content=content,
                file=uploaded_file,
                scheduled_for=scheduled_for,
            )
        return redirect("group_chat", group_id=group.id)

    messages_qs = group.messages.select_related("sender").prefetch_related('reactions').order_by("timestamp")
    visible_messages = [m for m in messages_qs if m.is_visible]
    MAX_INITIAL = 50
    if len(visible_messages) > MAX_INITIAL:
        visible_messages = visible_messages[-MAX_INITIAL:]
    # mark reads
    for m in visible_messages:
        GroupMessageRead.objects.get_or_create(message=m, user=request.user)
    dashboard_url_name = _user_dashboard_url_name(request.user)
    return render(request, "messagingApp/group_chat.html", {
        "group": group,
        "chat_messages": visible_messages,  # renamed to avoid clash with Django messages framework
        "dashboard_url_name": dashboard_url_name,
    })


# ------------- Message Search ---------------
@login_required
def search_messages(request):
    term = request.GET.get("q", "").strip()
    results_direct = []
    results_group = []
    if term:
        results_direct = Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user),
            content__icontains=term,
            scheduled_for__isnull=True
        ).order_by("-timestamp")[:50]
        group_ids = GroupMembership.objects.filter(user=request.user).values_list("group_id", flat=True)
        results_group = GroupMessage.objects.filter(
            group_id__in=group_ids,
            content__icontains=term,
            scheduled_for__isnull=True
        ).order_by("-timestamp")[:50]
    return render(request, "messagingApp/search.html", {
        "term": term,
        "results_direct": results_direct,
        "results_group": results_group,
        "dashboard_url_name": _user_dashboard_url_name(request.user),
    })


# ------------- Reactions API ---------------
@login_required
def react(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    emoji = request.POST.get("emoji")
    msg_type = request.POST.get("type")
    msg_id = request.POST.get("id")
    if not (emoji and msg_type and msg_id):
        return JsonResponse({"error": "Missing params"}, status=400)
    valid_emojis = [e for e, _ in Reaction._meta.get_field("emoji").choices]
    if emoji not in valid_emojis:
        return JsonResponse({"error": "Invalid emoji"}, status=400)
    model = Message if msg_type == "direct" else GroupMessage if msg_type == "group" else None
    if not model:
        return JsonResponse({"error": "Invalid type"}, status=400)
    obj = get_object_or_404(model, id=msg_id)
    # permission check
    if isinstance(obj, Message):
        if request.user.id not in [obj.sender_id, obj.receiver_id]:
            return JsonResponse({"error": "Forbidden"}, status=403)
    else:
        if not GroupMembership.objects.filter(group=obj.group, user=request.user).exists():
            return JsonResponse({"error": "Forbidden"}, status=403)
    ct = ContentType.objects.get_for_model(model)
    reaction_qs = Reaction.objects.filter(user=request.user, emoji=emoji, content_type=ct, object_id=obj.id)
    if reaction_qs.exists():
        reaction_qs.delete()
        action = "removed"
    else:
        Reaction.objects.create(user=request.user, emoji=emoji, content_type=ct, object_id=obj.id)
        action = "added"
    # aggregate counts
    aggregated = (Reaction.objects
                  .filter(content_type=ct, object_id=obj.id)
                  .values('emoji')
                  .annotate(count=Count('id'))
                  .order_by('emoji'))
    # Broadcast to room for realtime reaction update
    layer = get_channel_layer()
    if isinstance(obj, Message):
        room = f'direct_{min(obj.sender_id, obj.receiver_id)}_{max(obj.sender_id, obj.receiver_id)}'
    else:
        room = f'group_{obj.group_id}'
    async_to_sync(layer.group_send)(room, {
        'type': 'external.reaction',
        'message_id': obj.id,
        'reactions': list(aggregated),
    })
    return JsonResponse({
        "status": action,
        "reactions": list(aggregated),
        "message_id": obj.id,
    })


@login_required
def conversation_poll(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if request.user.id == other_user.id:
        return JsonResponse({"messages": []})
    # permission similar to conversation view
    allowed = False
    if request.user.role == "admin" and other_user.role in ["teacher", "parent"]:
        allowed = True
    elif request.user.role == "teacher" and other_user.role in ["parent", "admin"]:
        allowed = True
    elif request.user.role == "parent" and other_user.role in ["teacher", "admin"]:
        allowed = True
    if not allowed:
        return JsonResponse({"messages": []})
    after_id = request.GET.get('after')
    qs_base = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user)
    )
    stream = request.GET.get('stream') == '1'
    start_time = time.time()
    timeout = 25  # seconds for long-poll
    new_qs = Message.objects.none()
    while True:
        qs = qs_base
        if after_id and after_id.isdigit():
            qs = qs.filter(id__gt=int(after_id))
        new_qs = qs.select_related('sender').order_by('timestamp')[:200]
        if new_qs.exists() or not stream:
            break
        if time.time() - start_time > timeout:
            break
        time.sleep(1)
    ct = ContentType.objects.get_for_model(Message)
    data = []
    for m in new_qs:
        agg = (Reaction.objects.filter(content_type=ct, object_id=m.id)
               .values('emoji').annotate(count=Count('id')).order_by('emoji'))
        data.append({
            'id': m.id,
            'sender_id': m.sender_id,
            'sender_name': m.sender.get_full_name() or m.sender.username,
            'content': m.content,
            'file_url': m.file.url if m.file else None,
            'timestamp': m.timestamp.isoformat(),
            'reactions': list(agg),
        })
    return JsonResponse({"messages": data})


@login_required
def group_poll(request, group_id):
    group = get_object_or_404(GroupChat, id=group_id)
    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        return JsonResponse({"messages": []})
    after_id = request.GET.get('after')
    messages_qs = group.messages.select_related('sender').order_by('timestamp')
    stream = request.GET.get('stream') == '1'
    start_time = time.time()
    timeout = 25
    filtered = GroupMessage.objects.none()
    while True:
        qs = messages_qs
        if after_id and after_id.isdigit():
            qs = qs.filter(id__gt=int(after_id))
        filtered = qs[:200]
        if filtered.exists() or not stream:
            break
        if time.time() - start_time > timeout:
            break
        time.sleep(1)
    ct = ContentType.objects.get_for_model(GroupMessage)
    data = []
    for m in filtered:
        agg = (Reaction.objects.filter(content_type=ct, object_id=m.id)
               .values('emoji').annotate(count=Count('id')).order_by('emoji'))
        data.append({
            'id': m.id,
            'sender_id': m.sender_id,
            'sender_name': m.sender.get_full_name() or m.sender.username,
            'content': m.content,
            'file_url': m.file.url if m.file else None,
            'timestamp': m.timestamp.isoformat(),
            'reactions': list(agg),
        })
    return JsonResponse({"messages": data})


# ------------- AJAX / WS Upload Endpoints ---------------
@login_required
@require_POST
def upload_direct(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    # reuse permission logic
    allowed = False
    if request.user.role == "admin" and other_user.role in ["teacher", "parent"]:
        allowed = True
    elif request.user.role == "teacher" and other_user.role in ["parent", "admin"]:
        allowed = True
    elif request.user.role == "parent" and other_user.role in ["teacher", "admin"]:
        allowed = True
    if not allowed:
        return JsonResponse({"error": "forbidden"}, status=403)
    content = request.POST.get('content', '').strip()
    file = request.FILES.get('file')
    if not content and not file:
        return JsonResponse({"error": "empty"}, status=400)
    msg = Message.objects.create(sender=request.user, receiver=other_user, content=content, file=file)
    payload = {
        'id': msg.id,
        'sender_id': msg.sender_id,
        'sender_name': msg.sender.get_full_name() or msg.sender.username,
        'content': msg.content,
        'file_url': msg.file.url if msg.file else None,
        'timestamp': msg.timestamp.isoformat(),
    }
    # Broadcast via channel layer (room naming scheme mirrors consumer)
    room = f'direct_{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}'
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(room, { 'type': 'external.message', 'message': payload })
    return JsonResponse({'message': payload})


@login_required
@require_POST
def upload_group(request, group_id):
    group = get_object_or_404(GroupChat, id=group_id)
    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        return JsonResponse({"error": "forbidden"}, status=403)
    content = request.POST.get('content', '').strip()
    file = request.FILES.get('file')
    if not content and not file:
        return JsonResponse({"error": "empty"}, status=400)
    gm = GroupMessage.objects.create(group=group, sender=request.user, content=content, file=file)
    payload = {
        'id': gm.id,
        'sender_id': gm.sender_id,
        'sender_name': gm.sender.get_full_name() or gm.sender.username,
        'content': gm.content,
        'file_url': gm.file.url if gm.file else None,
        'timestamp': gm.timestamp.isoformat(),
    }
    room = f'group_{group.id}'
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(room, { 'type': 'external.message', 'message': payload })
    return JsonResponse({'message': payload})

