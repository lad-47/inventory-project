from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from home.models import Request, Cart_Request, Item, Log
from .forms import ServiceForm
from datetime import date
from django.contrib.auth.models import User

def manager_home(request):
	return render(request, 'manager/manager_home.html');

def cart_requests(request):
	#check if the user is a manager
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	#this duplicated code is necessary (I think) because of the
	#restrictive nature of calling things from a template
	cart_requests = Cart_Request.objects.filter(is_active_request=True);
	cart_requestsO = cart_requests.filter(cart_status='O');
	cart_requestsO_and_v = create_request_info(cart_requestsO);
	context = {
		'outstanding': cart_requestsO_and_v,
	}
	return render(request, 'manager/cart_requestsI.html', context)

def request_history(request):
	cart_requests = Cart_Request.objects.filter(is_active_request=True);
	cart_requestsA = cart_requests.filter(cart_status='A');
	cart_requestsD = cart_requests.filter(cart_status='D');
	cart_requestsA_and_v = create_request_info(cart_requestsA);
	cart_requestsD_and_v = create_request_info(cart_requestsD);
	context = {
		'approved': cart_requestsA_and_v,
		'denied': cart_requestsD_and_v,
	}
	return render(request, 'manager/request_history.html', context);


def create_request_info(cart_requests):
	cart_requests_and_v = [];
	for cart_request in cart_requests:
		subrequests = Request.objects.filter(parent_cart=cart_request);
		valid = True;
		for subrequest in subrequests:
			itemToChange = Item.objects.get(id=subrequest.item_id_id);
			oldQuantity = itemToChange.count;
			requestAmount = subrequest.quantity;
			newQuantity = oldQuantity - requestAmount;
			if newQuantity < 0:
				valid = False;
				break;
		cart_requests_and_v += [(cart_request, valid)];
	return cart_requests_and_v;

def create_indv_request_info(cart_request):
	subrequests = Request.objects.filter(parent_cart=cart_request);
	#assemble useful info to pass to template or use for db manipulation
	req_info = [];
	for subrequest in subrequests:
		itemToChange = Item.objects.get(id=subrequest.item_id_id);
		oldQuantity = itemToChange.count;
		requestAmount = subrequest.quantity;
		newQuantity = oldQuantity - requestAmount;
		valid = not (newQuantity < 0)
		req_info+=[(subrequest, requestAmount, oldQuantity, valid, itemToChange)];
	return req_info;


def cart_request_details(request, cart_request_id):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')

	current_request = get_object_or_404(Cart_Request, pk=cart_request_id);
	subrequests = Request.objects.filter(parent_cart_id=cart_request_id);
	
	#assemble useful info to pass to template or use for db manipulation
	req_info = create_indv_request_info(current_request);
	##handle the data from the form on a post
	if request.method == 'POST':
		service_form = ServiceForm(request.POST);
		if service_form.is_valid():
			if service_form.cleaned_data['approve_deny'] == 'Approve':
				current_request.cart_status='A';
				for el in req_info:
					if not el[3]:
						return HttpResponseRedirect('/manager/request_failure');
				for el in req_info:
					el[4].count = el[2]-el[1]; ##update item quantity
					el[0].status='A'; ##subrequest was serviced
					el[0].save();  ##save the subrequest's updated status
					el[4].save();  ##save the item with new quantity
			else:
				current_request.cart_status='D';
			current_request.admin_comment=service_form.cleaned_data['admin_comment'];
			current_request.save();
			return HttpResponseRedirect('/manager/request_success');

	##the form that will be sent to the template on a GET
	else:
		service_form = ServiceForm();

	context = {
		'current_request': current_request,
		'req_info': req_info,
		'service_form': service_form,
	}
	return render(request, 'manager/cart_request_details.html', context);

def request_success(request):
	return render(request, 'manager/request_success.html');

def request_failure(request):
	return render(request, 'manager/request_failure.html');


def old_cart_request_details(request, cart_request_id):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')

	current_request = get_object_or_404(Cart_Request, pk=cart_request_id);
	req_info = create_indv_request_info(current_request);

	context = {
		'current_request': current_request,
		'req_info': req_info,
	}
	return render(request, 'manager/old_cart_request_details.html', context);

def logs(request):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	logs = Log.objects.all()
	items = Item.objects.all()
	users = User.objects.all()
	if request.method == 'GET':  # If the form is submitted
		item_query = request.GET.get('item_box', None)
		user_query = request.GET.get('user_box', None)
		time_query = request.GET.get('date', None)
		if item_query is not None and not item_query=="":
			try:
				item = Item.objects.get(item_name=item_query)
				logs = logs.filter(involved_item=item.id)
			except Item.DoesNotExist:
				context = {
					'logs': logs,
					'items': items,
					'users': users,
					'error': "Item does not exist" }
				return render(request, 'manager/logs.html', context)
		if user_query is not None and not user_query=="":
			try:
				user = User.objects.get(username=user_query)
				logs = logs.filter(initiating_user=user.id)
			except User.DoesNotExist:
				context = {
					'logs': logs,
					'items': items,
					'users': users,
					'error': "User does not exist" }
				return render(request, 'manager/logs.html', context)
		if time_query is not None and not time_query=="":
			date_string = time_query.split("-")
			logs = logs.filter(timestamp__date__gte=date(int(date_string[0]),int(date_string[1]),int(date_string[2]))) 
	context = {
		'logs': logs,
		'items': items,
		'users': users
	}
	return render(request, 'manager/logs.html', context)

