from django.conf.urls import url
from credoweb import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'user/(?P<name>[a-zA-Z0-9]{1,24})/$', views.user)
]
