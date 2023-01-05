# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import re_path

from credoapiv2 import views

urlpatterns = [
    re_path(r"^user/register$", views.UserRegistrationView.as_view()),
    re_path(r"^user/login$", views.UserLoginView.as_view()),
    re_path(r"^user/oauth_login$", views.UserOAuthLoginView.as_view()),
    re_path(r"^user/info$", views.UserInfoView.as_view()),
    re_path(r"^user/id$", views.UserIdView.as_view()),
    re_path(r"^user/delete_account$", views.UserDeleteAccount.as_view()),
    re_path(r"^detection$", views.DetectionView.as_view()),
    re_path(r"^ping$", views.PingView.as_view()),
    re_path(r"^data_export$", views.DataExportView.as_view()),
    re_path(r"^mapping_export$", views.MappingExportView.as_view()),
]
