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
	url(r'^tag_handler/$', views.tag_handler, name="tag handler"),
	url(r'^tag_handler/create/$', views.create_tag, name="create tag"),
	url(r'^tag_handler/modify/$', views.modify_tag, name="modify tag"),
	url(r'^tag_success/$', views.tag_success, name="tag success"),
	url(r'^tag_handler/delete_1/$', views.delete_tag_conf, name="delete tag conf"),
	url(r'^tag_handler/delete_2/$', views.delete_tag_action, name="delete tag action"),
	url(r'^tag_delete_success/$', views.tag_delete_success, name="tag delete success"),
	url(r'^direct_disburse/$', views.direct_disburse, name="direct-disburse"),
	#url(r'^cart_request/(?P<cart_request_id>[0-9]+$)', \
		#views.cart_request_details, name="cart request details"),
]

#(?P<cart_request_id>[0-9]+$)