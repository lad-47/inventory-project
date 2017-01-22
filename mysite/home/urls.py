from django.conf.urls import url

from . import views

app_name = 'home'
urlpatterns = [
	# ex: /home/
    url(r'^$', views.index, name='index'),
	# ex: /home/5/
    url(r'^(?P<item_id>[0-9]+)/$', views.detail, name='detail'),
]