from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required, permission_required

from . import views

app_name = 'home'

urlpatterns = [
    url(r'^(?P<item_id>[0-9]+)/$', views.detail, name='detail'),
    
    url(r'^login/$', auth_views.login, name="login"),
    url(r'^logout/$', auth_views.logout,name='logout'),
    url(r'^(?P<item_id>[0-9]+)/request/$', views.request, name='request'),
    url(r'^delete/(?P<pk>\d+)/$', views.DeleteRequestView.as_view(),
        name='request-delete'),
    url(r'^requests/$', views.requestsView.as_view(), name='requests'),
    url(r'^all_requests/$', permission_required('home.can_service')\
        (views.serviceRequestsView.as_view()), name='service'),
    ##this is hacked over the automatic destination of denying permission
    url(r'^accounts/login/$', views.cannotService, name='cant_service'),
    url(r'^request/(?P<request_id>[0-9]+)/$', views.request_details, name='service form'),
    url(r'^request/(?P<request_id>[0-9]+)/service/$', views.service_request, \
        name='service request form'),
]