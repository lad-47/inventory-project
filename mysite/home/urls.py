from django.conf.urls import url

from . import views

from .views import ItemListView

app_name = 'home'
urlpatterns = [
	# ex: /home/
    url(r'^$', ItemListView.as_view(), name='index'),
	# ex: /home/5/
    url(r'^(?P<item_id>[0-9]+)/$', views.detail, name='detail'),
]