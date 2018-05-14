from django.conf.urls import url
from credoweb import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'user/(?P<username>.{1,50})/$', views.user_page, name='user_page'),
    url(r'user/(?P<username>.{1,50})/(?P<page>\w+)$', views.user_page, name='user_page_paginated'),
    url(r'team/(?P<name>.{0,50})/$', views.team_page, name='team_page'),
    url(r'confirm_email/(?P<token>[a-z0-9]{64})/$', views.confirm_email, name='confirm_email'),
]
