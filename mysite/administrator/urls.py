from django.shortcuts import render
from django.conf.urls import include, url

from . import views


urlpatterns = [
    url(r'^users/$', views.users, name='users'),
    url(r'^create_user/$', views.create_user, name='create-user'),
    url(r'^user-detail/(?P<user_id>[0-9]+)/$', views.detail_user, name='detail-user'),
]