from django.conf.urls import url
from . import consumers


public_routing=[
    url(r'^ws/model/',consumers.WSConsumer),
]
