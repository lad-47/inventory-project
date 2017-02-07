from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Item, Request, Tag;
from .forms import ServiceReqForm;

def index(request):
    latest_item_list = Item.objects.order_by('id')[:5]
    context = {
        'latest_item_list': latest_item_list,
    }
    return render(request, 'home/index.html', context)
	
def detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'home/detail.html', {'item': item})

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

class requestsView(LoggedInMixin, RequestOwnerMixin, generic.ListView):
	model = Request;
	context_object_name = 'request_list';
	template_name = 'home/requests.html';

	def get_queryset(self):
		return Request.objects.filter(owner=self.request.user);

class serviceRequestsView(LoggedInMixin, generic.ListView):
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
	