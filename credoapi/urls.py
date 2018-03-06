from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from credoapi import views

urlpatterns = [
    url(r'^$', views.handle_detection)
]

# urlpatterns = format_suffix_patterns(urlpatterns)