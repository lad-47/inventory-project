from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required, permission_required
import home.views as views
import mysite.oauth_views as oauth_views
from django.views.generic import RedirectView
import home.api_views as api_views
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls.static import static
from django.conf import settings
#from ctypes.test.test_pickling import name

urlpatterns = [
    #3 apps, separated primarily by permissions
    url(r'^', include('home.urls')),
    url(r'^manager/', include('manager.urls')),
    url(r'^admin/', include('administrator.urls')),
    url(r'^admin/delete_item/(?P<item_id>[0-9]+)/$', views.delete_item, name='delete item'),
    url(r'^admin/delete_item/(?P<item_id>[0-9]+)/confirm/$', views.delete_check, name='delete check'),
    url(r'^login/$', auth_views.login, name="login"),
    url(r'^logout/$', auth_views.logout,name='logout'),
    url(r'^developers/', views.developers, name='developers'),
    url(r'^api_download/', views.api_download, name='api-download'),
    url(r'^accounts/login/duke/$', RedirectView.as_view(url='https://oauth.oit.duke.edu/oauth/authorize.php?response_type=code&client_id=inventory&scope=identity%%3Anetid%%3Aread&redirect_uri=https%%3A%%2F%%2Fcolab-sbx-44.oit.duke.edu%%2Faccounts%%2Fcallback%%2Fduke%%2F&state=basic'), name='allaccess-login'),
    url(r'^accounts/callback/duke/$', oauth_views.callback, name='allaccess-callback'),
    url(r'^api/item/$', api_views.item_list, name='item-list'),
    url(r'^api/item/(?P<pk>[0-9]+)$', api_views.item_detail, name='item-detail'),
    url(r'^api/request/$', api_views.request_list, name='request-list'),
    url(r'^api/request/(?P<pk>[0-9]+)$', api_views.request_detail, name='request-detail'),
    url(r'^api/user/$', api_views.user_list, name='user-list'),
    url(r'^api/user/(?P<pk>[0-9]+)$', api_views.user_detail, name='user-detail'),
    url(r'^api/user/create$', api_views.user_create, name='user-create'),
    url(r'^api/$', api_views.api_root, name='api'),
    url(r'^api/custom_fields/$', api_views.custom_root, name='api-custom'),
    url(r'^api/short$', api_views.short_list, name='short-list'),
    url(r'^api/short/(?P<pk>[0-9]+)$', api_views.short_detail, name='short-detail'),
    url(r'^api/long$', api_views.long_list, name='long-list'),
    url(r'^api/long/(?P<pk>[0-9]+)$', api_views.long_detail, name='long-detail'),
    url(r'^api/int$', api_views.int_list, name='int-list'),
    url(r'^api/int/(?P<pk>[0-9]+)$', api_views.int_detail, name='int-detail'),
    url(r'^api/float$', api_views.float_list, name='float-list'),
    url(r'^api/float/(?P<pk>[0-9]+)$', api_views.float_detail, name='float-detail'),
    url(r'^api/entry$', api_views.custom_list, name='custom-list'),
    url(r'^api/entry/(?P<pk>[0-9]+)$', api_views.custom_detail, name='custom-detail'),
    url(r'^api/logs$', api_views.log_list, name='log-list'),
    url(r'^token/$', api_views.get_token, name='get-token'),
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]

urlpatterns += staticfiles_urlpatterns()

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
