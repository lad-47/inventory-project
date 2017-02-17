"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required, permission_required
import home.views as views
import home.api_views as api_views
from rest_framework.urlpatterns import format_suffix_patterns
from ctypes.test.test_pickling import name


## refactor application urls when necessary
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<item_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^admin/', admin.site.urls),
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
    url(r'^api/item/$', api_views.item_list, name='item-list'),
    url(r'^api/item/(?P<pk>[0-9]+)$', api_views.item_detail, name='item-detail'),
    url(r'^api/request/$', api_views.request_list, name='request-list'),
    url(r'^api/request/(?P<pk>[0-9]+)$', api_views.request_detail, name='request-detail'),
    url(r'^api/user/$', api_views.user_list, name='user-list'),
    url(r'^api/user/(?P<pk>[0-9]+)$', api_views.user_detail, name='user-detail'),
    url(r'^api/user/create$', api_views.user_create, name='user-create'),
    url(r'^api/$', api_views.api_root),
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]

urlpatterns += staticfiles_urlpatterns()

urlpatterns = format_suffix_patterns(urlpatterns)
