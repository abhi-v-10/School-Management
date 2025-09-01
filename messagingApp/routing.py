from django.urls import path
from .consumers import DirectChatConsumer, GroupChatConsumer

websocket_urlpatterns = [
    path('ws/chat/<int:user_id>/', DirectChatConsumer.as_asgi()),
    path('ws/group/<int:group_id>/', GroupChatConsumer.as_asgi()),
]
