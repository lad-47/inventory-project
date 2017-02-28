from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required, permission_required

from . import views

urlpatterns = [

    #these are our old urls that were in mysite.urls
    #they will all end up the same as they were, since
    #the prefix for them is just '^' before the include
    url(r'^$', views.index, name='index'),
    url(r'^(?P<item_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<item_id>[0-9]+)/request/$', views.request, name='request'),
    #url(r'^delete/(?P<pk>\d+)/$', views.DeleteRequestView.as_view(),
       # name='request-delete'),
    url(r'^requests/$', views.requestsView.as_view(), name='requests'),
    url(r'^delete_request/(?P<cart_request_id>[0-9]+)/$', views.delete_request, name='delete request'),
    url(r'^delete_request_success/$', views.delete_request_success, \
        name='delete request success'),
    #url(r'^all_requests/$', permission_required('home.can_service')\
    #    (views.serviceRequestsView.as_view()), name='service'),
    ##this is hacked over the automatic destination of denying permission
    #url(r'^accounts/login/$', views.cannotService, name='cant_service'),
    url(r'^request_details/(?P<cart_request_id>[0-9]+)/$', views.cart_request_details,\
     name='view request details'),
    url(r'^checkout_success/$', views.checkout_success, name='checkout success'),
    url(r'^checkout/$', views.checkout, name='checkout'),
    url(r'^remove_request/(?P<request_id>[0-9]+)/$', views.remove_request, name='remove subrequest'),

    #url(r'^request/(?P<request_id>[0-9]+)/$', views.request_details, name='service form'),
    #url(r'^request/(?P<request_id>[0-9]+)/service/$', views.service_request, \
     #   name='service request form'),
]