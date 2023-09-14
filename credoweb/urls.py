from django.urls import include, re_path
from credoweb import views

urlpatterns = [
    re_path(r"^$", views.index, name="index"),
    re_path(r"faq/$", views.faq, name="faq"),
    re_path(r"rules/$", views.rules, name="rules"),
    re_path(r"detection_list/$", views.detection_list, name="detection_list"),
    re_path(r"detection_list/(?P<page>\w+)/$", views.detection_list, name="detection_list"),
    re_path(r"user/(?P<username>.{1,50})/$", views.user_page, name="user_page"),
    re_path(
        r"user/(?P<username>.{1,50})/(?P<page>\w+)$",
        views.user_page,
        name="user_page_paginated",
    ),
    re_path(r"user_list/$", views.user_list, name="user_list"),
    re_path(r"user_list/(?P<page>\w+)/$", views.user_list, name="user_list"),
    re_path(r"team_list/$", views.team_list, name="team_list"),
    re_path(r"team_list/(?P<page>\w+)/$", views.team_list, name="team_list"),
    re_path(r"team/(?P<name>.{0,50})/$", views.team_page, name="team_page"),
    re_path(r"register/$", views.register, name="register"),
    re_path(
        r"confirm_email/(?P<token>[a-z0-9]{64})/$",
        views.confirm_email,
        name="confirm_email",
    ),
    re_path("^", include("django.contrib.auth.urls")),
]
