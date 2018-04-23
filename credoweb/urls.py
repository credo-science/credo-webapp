from django.conf.urls import url
from credoweb import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'user/(?P<username>[a-zA-Z0-9]{1,150})/$', views.user_page, name='user_page'),
    url(r'team/(?P<name>[a-zA-Z0-9]{1,255})/$', views.team_page, name='team_page'),
    url(r'confirm_email/(?P<token>[a-z0-9]{64})/$', views.confirm_email, name='confirm_email'),
]
