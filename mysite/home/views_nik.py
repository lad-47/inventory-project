from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Item

"""
def index(request):
    latest_item_list = Item.objects.order_by('id')[:5]
    context = {
        'latest_item_list': latest_item_list,
    }
    return render(request, 'home/index.html', context)
	
def detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'home/detail.html', {'item': item})
"""

"""
Classes that inherit from this require the user to be logged in.
"""
class LoggedInMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)

"""
All Item List View (Index View):
 - displays the list of all items
"""
class AllItemListView(LoggedInMixin, generic.ListView):
	template_name = 'home/index.html'
	context_object_name = 'item_list'

	def get_queryset(self):
		"""Return all items."""
		return Item.objects.order_by('id')[]

"""
Latest Item List View (Index View):
 - displays a list of the first 5 items by id
"""
class LatestItemListView(LoggedInMixin, generic.ListView):
	template_name = 'home/index.html'
	context_object_name = 'latest_item_list'

	def get_queryset(self):
		"""Return the first five items by id."""
		return Item.objects.order_by('id')[:5]

class DetailView(LoggedInMixin, generic.DetailView):
	model = Item
	template_name = 'home/detail.html'