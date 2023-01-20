"""credo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import re_path, include
from django.conf import settings
from django.contrib import admin
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView

from rest_framework.documentation import include_docs_urls

urlpatterns = [
    re_path(r"^$", RedirectView.as_view(url="web/")),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^web/", include("credoweb.urls")),
    re_path(r"^api/v2/", include("credoapiv2.urls")),
    re_path(r"^acra/", include("acra.urls")),
    re_path(r"^django-rq/", include("django_rq.urls")),
    re_path(r"^docs/", include_docs_urls(title="CREDO API documentation")),
    re_path(r"^robots.txt",TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [re_path(r"__debug__/", include(debug_toolbar.urls))] + urlpatterns
