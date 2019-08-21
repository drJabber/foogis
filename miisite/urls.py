from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',view=views.hello,name='hello'),
    url(r'tofile/$',view=views.tofile,name='tofile'),
    url(r'^start/$',view=views.start,name='start'),
    url(r'^stop/$',view=views.stop,name='stop'),
    url(r'^pause/$',view=views.pause,name='pause'),
    url(r'^resume/$',view=views.resume,name='resume'),
]
