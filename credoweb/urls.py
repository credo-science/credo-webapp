from django.conf.urls import url
from credoweb import views

urlpatterns = [
    url(r'^$', views.index)
]