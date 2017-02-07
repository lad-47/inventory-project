from django.http import HttpResponse, Http404, HttpResponseR
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Item, Request, Tag;
from .forms import ServiceReqForm;
#chance genereic.Listview stuff to ListView
from django.views.generic import View, DetailView, ListView, CreateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse

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

class LoggedInMixin(object):

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(LoggedInMixin, self).dispatch(*args, **kwargs);

class RequestOwnerMixin(object):

	def get_object(self, queryset=None):

		if queryset is None:
			queryset = self.get_queryset();

		pk = self.kwargs.get(self.pk_url_kwarg, None);
		queryset = querysetfilter(
			pk=pk,
			owner=self.request.user,);

		try:
			obj = queryset.get();
		except ObjectDoesNotExist:
			raise PermsisionDenied
		return obj

class requestsView(LoggedInMixin, RequestOwnerMixin, ListView):
	model = Request;
	context_object_name = 'request_list';
	template_name = 'home/requests.html';

	def get_queryset(self):
		return Request.objects.filter(owner=self.request.user);

class serviceRequestsView(LoggedInMixin, ListView):
	model = Request;
	context_object_name = 'request_list';

	template_name = 'home/service.html';
	def get_queryset(self):
		return Request.objects.filter(status='O');

def cannotService(request):
	return render(request, 'home/notAdmin.html'); 

def service_request(request):
	if request.method == 'POST':
		form = ServiceReqForm(request.POST);

		if form.is_valid():
			return HttpResponseRedirect('/processed/');
	else:
		form = ServiceReqForm();
		return render(request, 'home/serviceReq.html', {'form:': form})
	
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

class DeleteRequestView(DeleteView):
    model = Request
    template_name = 'home/delete_request.html'
    
    def get_success_url(self):
        return reverse('index')

# class ListItemView(ListView):
#     model=Item
#     template_name='home/index.html'
# 
# class ItemDetailView(DetailView):
#     model=Item
#     template_name='home/detail.html'
