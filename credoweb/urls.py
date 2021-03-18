from django.conf.urls import url
from credoweb import views
from django.conf.urls import include

urlpatterns = [
    url(r"^$", views.index, name="index"),
    url(r"faq/$", views.faq, name="faq"),
    url(r"detection_list/$", views.detection_list, name="detection_list"),
    url(r"detection_list/(?P<page>\w+)/$", views.detection_list, name="detection_list"),
    url(r"user/(?P<username>.{1,50})/$", views.user_page, name="user_page"),
    url(
        r"user/(?P<username>.{1,50})/(?P<page>\w+)$",
        views.user_page,
        name="user_page_paginated",
    ),
    url(r"user_list/$", views.user_list, name="user_list"),
    url(r"user_list/(?P<page>\w+)/$", views.user_list, name="user_list"),
    url(r"team_list/$", views.team_list, name="team_list"),
    url(r"team_list/(?P<page>\w+)/$", views.team_list, name="team_list"),
    url(r"team/(?P<name>.{0,50})/$", views.team_page, name="team_page"),
    url(r"register/$", views.register, name="register"),
    url(
        r"confirm_email/(?P<token>[a-z0-9]{64})/$",
        views.confirm_email,
        name="confirm_email",
    ),
    url("^", include("django.contrib.auth.urls")),
]
