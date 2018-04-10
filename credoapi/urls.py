from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from credoapi import views

urlpatterns = [
    url(r'^$', views.FrameHandler.as_view())
]

# urlpatterns = format_suffix_patterns(urlpatterns)