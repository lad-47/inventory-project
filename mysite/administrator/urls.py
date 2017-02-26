from django.shortcuts import render
from django.conf.urls import include, url

from . import views


urlpatterns = [
    url(r'^users/$', views.users, name='users'),
    url(r'^create_user/$', views.create_user, name='create-user'),
    url(r'^user-detail/(?P<user_id>[0-9]+)/$', views.detail_user, name='detail-user'),
    url(r'^custom_fields/$', views.cf_manager, name='custom field manager'),
    url(r'^custom_fields/delete_conf/$', views.cf_delete_conf, name='cf delete conf'),
    url(r'^custom_fields/delete_action/$', views.cf_delete_action, name='cf delete action'),
    url(r'^custom_fields/create/success/$', views.cf_create_success, name='cf create success'),
    url(r'^custom_fields/delete/success/$', views.cf_delete_success, name='cf delete success'),
]