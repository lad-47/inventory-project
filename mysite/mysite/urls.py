from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required, permission_required

from home import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^', include('home.urls')),
    url(r'^manager/', include('manager.urls')),
    url(r'^admin/', admin.site.urls),
]