from django.conf.urls import url

from acra import views

urlpatterns = [
    url(r'^report$', views.report),
]
