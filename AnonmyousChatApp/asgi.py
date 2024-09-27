"""
ASGI config for AnonmyousChatApp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AnonmyousChatApp.settings')

# Initialize the HTTP application (for Django HTTP handling)
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    # WebSocket part (lazy loading the websocket routes)
    'websocket': URLRouter(
        # Importing ws_urlpatterns here to make sure apps are loaded
        __import__('ChatApp.routing').routing.ws_urlpatterns
    ),
})

# Alias app for compatibility
app = application
