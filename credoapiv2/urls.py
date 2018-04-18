from django.conf.urls import url

from credoapiv2 import views

urlpatterns = [
    url(r'^user$', views.ManageUser.as_view()),
    url(r'^user$', views.ManageDetection.as_view())
]
