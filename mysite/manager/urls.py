from django.shortcuts import render
from django.conf.urls import include, url

from . import views


urlpatterns = [
	url(r'^$', views.manager_home, name='manager_home'),
	url(r'^cart_requests/', views.cart_requests, name='cart requests'),
	url(r'^cart_request_details/(?P<cart_request_id>[0-9]+)/$', \
		views.cart_request_details,	name="cart request details"),
	#url(r'^cart_request/(?P<cart_request_id>[0-9]+$)', \
		#views.cart_request_details, name="cart request details"),
]

#(?P<cart_request_id>[0-9]+$)