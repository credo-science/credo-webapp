from django.conf.urls import url

from credoapiv2 import views

urlpatterns = [
    url(r'^user/register$', views.ManageUserRegistration.as_view()),
    url(r'^user/login$', views.ManageUserLogin.as_view()),
    url(r'^detection$', views.ManageDetection.as_view()),
    url(r'^ping$', views.ManageDetection.as_view()),
]
