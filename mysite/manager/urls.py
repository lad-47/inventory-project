from django.shortcuts import render
from django.conf.urls import include, url

from . import views


urlpatterns = [
	url(r'^$', views.manager_home, name='manager_home'),
]