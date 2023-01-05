from django.urls import re_path

from acra import views

urlpatterns = [re_path(r"^report$", views.report)]
