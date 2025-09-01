from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from .models import Message, GroupChat, GroupMessage, GroupMembership, Reaction
from django.utils import timezone

User = get_user_model()

# Helper db funcs
@database_sync_to_async
def fetch_recent_direct(user_id, other_id, limit=50, before=None):
    qs = Message.objects.filter(Q(sender_id=user_id, receiver_id=other_id) | Q(sender_id=other_id, receiver_id=user_id)).order_by('-id')
    if before:
        qs = qs.filter(id__lt=before)
    msgs = list(qs.select_related('sender')[:limit])
    data = []
    for m in reversed(msgs):
        data.append({
            'id': m.id,
            'sender_id': m.sender_id,
            'sender_name': m.sender.get_full_name() or m.sender.username,
            'content': m.content,
            'file_url': m.file.url if m.file else None,
            'timestamp': m.timestamp.isoformat(),
        })
    return data

@database_sync_to_async
def create_direct_message(sender_id, other_id, content, file=None):
    m = Message.objects.create(sender_id=sender_id, receiver_id=other_id, content=content, file=file)
    return m.id

@database_sync_to_async
def fetch_recent_group(group_id, limit=50, before=None):
    qs = GroupMessage.objects.filter(group_id=group_id).order_by('-id')
    if before:
        qs = qs.filter(id__lt=before)
    msgs = list(qs.select_related('sender')[:limit])
    data = []
    for m in reversed(msgs):
        data.append({
            'id': m.id,
            'sender_id': m.sender_id,
            'sender_name': m.sender.get_full_name() or m.sender.username,
            'content': m.content,
            'file_url': m.file.url if m.file else None,
            'timestamp': m.timestamp.isoformat(),
        })
    return data

@database_sync_to_async
def create_group_message(group_id, sender_id, content, file=None):
    m = GroupMessage.objects.create(group_id=group_id, sender_id=sender_id, content=content, file=file)
    return m.id

class DirectChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
            return
        self.other_id = int(self.scope['url_route']['kwargs']['user_id'])
        # Basic permission parity with view logic (simplified)
        me = self.scope['user']
        try:
            other = await database_sync_to_async(User.objects.get)(id=self.other_id)
        except User.DoesNotExist:
            await self.close(); return
        allowed = False
        if me.role == 'admin' and other.role in ['teacher','parent']:
            allowed = True
        elif me.role == 'teacher' and other.role in ['parent','admin']:
            allowed = True
        elif me.role == 'parent' and other.role in ['teacher','admin']:
            allowed = True
        if not allowed:
            await self.close(); return
        self.room_name = f'direct_{min(self.scope["user"].id, self.other_id)}_{max(self.scope["user"].id, self.other_id)}'
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        # initial recent messages
        recent = await fetch_recent_direct(self.scope['user'].id, self.other_id)
        await self.send_json({'type':'init', 'messages': recent})

    async def receive_json(self, content, **kwargs):
        action = content.get('action')
        if action == 'send':
            text = content.get('content','').strip()
            if text:
                mid = await create_direct_message(self.scope['user'].id, self.other_id, text)
                await self.channel_layer.group_send(self.room_name, {'type':'broadcast.message','mid':mid})
        elif action == 'load_older':
            before = content.get('before')
            older = await fetch_recent_direct(self.scope['user'].id, self.other_id, before=before)
            await self.send_json({'type':'older', 'messages': older})
        elif action == 'typing':
            await self.channel_layer.group_send(self.room_name, {'type':'typing.event','user': self.scope['user'].id})

    async def broadcast_message(self, event):
        mid = event['mid']
        # fetch single message details
        msgs = await fetch_recent_direct(self.scope['user'].id, self.other_id, limit=1, before=None)
        if msgs:
            await self.send_json({'type':'new', 'message': msgs[-1]})

    async def typing_event(self, event):
        if event['user'] != self.scope['user'].id:
            await self.send_json({'type':'typing', 'user_id': event['user']})

    async def external_message(self, event):
        # message payload already prepared by HTTP view
        await self.send_json({'type':'new', 'message': event['message']})

    async def external_reaction(self, event):
        await self.send_json({'type':'reaction', 'message_id': event['message_id'], 'reactions': event['reactions']})

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

class GroupChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close(); return
        self.group_id = int(self.scope['url_route']['kwargs']['group_id'])
        # membership check
        is_member = await database_sync_to_async(GroupMembership.objects.filter(group_id=self.group_id, user=self.scope['user']).exists)()
        if not is_member:
            await self.close(); return
        self.room_name = f'group_{self.group_id}'
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        recent = await fetch_recent_group(self.group_id)
        await self.send_json({'type':'init','messages':recent})

    async def receive_json(self, content, **kwargs):
        action = content.get('action')
        if action == 'send':
            text = content.get('content','').strip()
            if text:
                mid = await create_group_message(self.group_id, self.scope['user'].id, text)
                await self.channel_layer.group_send(self.room_name, {'type':'broadcast.message','mid':mid})
        elif action == 'load_older':
            before = content.get('before')
            older = await fetch_recent_group(self.group_id, before=before)
            await self.send_json({'type':'older','messages':older})
        elif action == 'typing':
            await self.channel_layer.group_send(self.room_name, {'type':'typing.event','user':self.scope['user'].id})

    async def broadcast_message(self, event):
        msgs = await fetch_recent_group(self.group_id, limit=1)
        if msgs:
            await self.send_json({'type':'new','message':msgs[-1]})

    async def typing_event(self, event):
        if event['user'] != self.scope['user'].id:
            await self.send_json({'type':'typing','user_id':event['user']})

    async def external_message(self, event):
        await self.send_json({'type':'new','message':event['message']})

    async def external_reaction(self, event):
        await self.send_json({'type':'reaction','message_id':event['message_id'],'reactions':event['reactions']})

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
