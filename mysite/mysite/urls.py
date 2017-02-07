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

## refactor application urls when necessary
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<item_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, name="login"),
    url(r'^logout/$', auth_views.logout,name='logout'),
    url(r'^requests/$', views.requestsView.as_view(), name='requests'),
    url(r'^all_requests/$', permission_required('home.can_service')\
        (views.serviceRequestsView.as_view()), name='service'),
    ##this is hacked over the automatic destination of denying permission
    url(r'^accounts/login/$', views.cannotService, name='cant_service'),
    url(r'^service_request/$', views.service_request, name='service form'),
    url(r'^(?P<item_id>[0-9]+)/request/$', views.request, name='request')
]


urlpatterns += staticfiles_urlpatterns()