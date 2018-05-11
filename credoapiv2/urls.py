from django.conf.urls import url

from credoapiv2 import views

urlpatterns = [
    url(r'^user/register$', views.UserRegistrationView.as_view()),
    url(r'^user/login$', views.UserLoginView.as_view()),
    url(r'^user/info$', views.UserInfoView.as_view()),
    url(r'^detection$', views.DetectionView.as_view()),
    url(r'^ping$', views.PingView.as_view()),
]
