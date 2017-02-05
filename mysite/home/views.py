from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic import View, DetailView, ListView, CreateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse

from .models import Item, Request

# def index(request):
#     latest_item_list = Item.objects.order_by('id')[:5]
#     context = {
#         'latest_item_list': latest_item_list,
#     }
#     return render(request, 'home/index.html', context)
# 	
def detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'home/detail.html', {'item': item})

def request(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    new_request = Request(user_id=request.user,item_id=item,reason=request.POST['reason'],status='O')
    new_request.save()
    return HttpResponse("success")

class ListItemView(ListView):
    model=Item
    template_name='home/index.html'

class ItemDetailView(DetailView):
    model=Item
    template_name='home/detail.html'
    