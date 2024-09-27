from django.urls import path
from . import consumers

ws_urlpatterns=[
    path("ws",consumers.MyConsumer.as_asgi()),
]