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
<<<<<<< HEAD
from django.contrib.auth.decorators import login_required, permission_required
from home import views as views2
=======
import home.views as views
>>>>>>> 9dea7098155533c6bdaefe6ce2241f9a99b04511

## refactor application urls when necessary
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<item_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, name="login"),
    url(r'^logout/$', auth_views.logout,name='logout'),
<<<<<<< HEAD
    url(r'^requests/$', views2.requestsView.as_view(), name='requests'),
    url(r'^service/$', permission_required('home.can_service')\
        (views2.serviceRequestsView.as_view()), name='service'),
    url(r'^accounts/login/$', views2.cannotService, name='cant_service'),
    url(r'^service_request/$', views2.service_request, name='service form')
=======
    url(r'^(?P<item_id>[0-9]+)/request/$', views.request, name='request')
>>>>>>> 9dea7098155533c6bdaefe6ce2241f9a99b04511
]


urlpatterns += staticfiles_urlpatterns()