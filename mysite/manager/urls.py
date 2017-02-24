from django.shortcuts import render
from django.conf.urls import include, url

from . import views


urlpatterns = [
	url(r'^$', views.manager_home, name='manager_home'),
	url(r'^cart_requests/$', views.cart_requests, name='cart requests'),
	url(r'^cart_request_details/(?P<cart_request_id>[0-9]+)/$', \
		views.cart_request_details,	name="cart request details"),
	url(r'^cart_request_history/$', views.request_history, name="request history"),
	url(r'^old_cart_request_details/(?P<cart_request_id>[0-9]+)/$', \
		views.old_cart_request_details, name="old cart request details"),
	url(r'^request_success/$', views.request_success, name="request success"),
	url(r'^request_failure/$', views.request_failure, name="request failure"),
	url(r'^logs/$', views.logs, name="logs"),
	url(r'^modify_an_item/(?P<item_id>[0-9]+)/$', views.modify_an_item, name="modify_an_item"),
	url(r'^update_success/$', views.update_success, name="update_success"),
	url(r'^add_an_item/$', views.add_an_item, name="add an item"),
	url(r'^create_success/$', views.create_success, name="create success"),
	#url(r'^cart_request/(?P<cart_request_id>[0-9]+$)', \
		#views.cart_request_details, name="cart request details"),
]

#(?P<cart_request_id>[0-9]+$)