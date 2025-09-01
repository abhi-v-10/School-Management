"""
ASGI config for managementProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'managementProject.settings')

from django.core.asgi import get_asgi_application  # noqa: E402

# Initialize Django (sets up apps) BEFORE importing routing/consumers
django_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402,E401
from channels.auth import AuthMiddlewareStack  # noqa: E402,E401
from messagingApp import routing as messaging_routing  # noqa: E402,E401

application = ProtocolTypeRouter({
	'http': django_app,
	'websocket': AuthMiddlewareStack(URLRouter(messaging_routing.websocket_urlpatterns)),
})
