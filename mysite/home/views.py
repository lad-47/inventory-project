from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views import generic

from .models import Item, Request, Tag;


def index(request):
    latest_item_list = Item.objects.order_by('id')[:5]
    context = {
        'latest_item_list': latest_item_list,
    }
    return render(request, 'home/index.html', context)
	
def detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'home/detail.html', {'item': item})

class requestsView(generic.ListView):
	model = Request;
	context_object_name = 'request_list';
	template_name = 'home/requests.html';

	def get_queryset(self):
		return Request.objects.all();
	