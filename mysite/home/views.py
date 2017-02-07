from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic import View, DetailView, ListView, CreateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse

from .models import Item, Request, Tag

def index(request):
    latest_item_list = Item.objects.order_by('id')[:5]
    tag_list = Tag.objects.distinct('tag')
    if request.method == 'GET': # If the form is submitted
        latest_item_list = Item.objects.all()
        search_query = request.GET.get('search_box', None)
        tag_query = request.GET.get('select', None)
        if search_query is not None:
            latest_item_list = latest_item_list.filter(item_name__icontains=search_query)
        if tag_query is not None and tag_query!='all':
            latest_item_list = latest_item_list.filter(tag__tag=tag_query)
    context = {
        'latest_item_list': latest_item_list,
        'tag_list': tag_list
    }
    return render(request, 'home/index.html', context)
 	
def detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if not request.user.is_authenticated():
        return render(request, 'home/detail.html', {'item':item})
    requests = Request.objects.filter(item_id=item.id,user_id=request.user)
    context = {
        'item': item,
        'requests': requests  
    }
    return render(request, 'home/detail.html', context)

def request(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    new_request = Request(user_id=request.user,item_id=item,reason=request.POST['reason'],status='O')
    new_request.save()
    return HttpResponse("success")

# class ListItemView(ListView):
#     model=Item
#     template_name='home/index.html'
# 
# class ItemDetailView(DetailView):
#     model=Item
#     template_name='home/detail.html'
    