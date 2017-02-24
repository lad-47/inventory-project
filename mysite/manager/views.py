from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from home.models import Request, Cart_Request, User, Item, Tag, CustomFieldEntry, \
CustomShortTextField, CustomLongTextField, CustomIntField, CustomFloatField
from .forms import ServiceForm, ItemForm_factory
from django.core.exceptions import ObjectDoesNotExist

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


def updateItem(item_instance, data):
	for field in data.keys():
		
		# we have to parse the tags by hand
		if field == 'tags':
			continue;

		# the getattr is a hacky way of getting it to throw an AttributeError
		try:
			getattr(item_instance, field);
			setattr(item_instance, field, data[field]);

		# AttributeError should mean it's a custom field
		# I have no idea why it throws ValueError for customs...
		except AttributeError as ex:
			field_entry = CustomFieldEntry.objects.get(field_name=field);
			field_type = field_entry.value_type;
			try:
				if field_type == 'st':
					to_change = CustomShortTextField.objects.get(parent_item=item_instance,\
						field_name=field_entry)
				elif field_type == 'lt':
					to_change = CustomLongTextField.objects.get(parent_item=item_instance,\
						field_name=field_entry)
				elif field_type == 'int':
					to_change = CustomIntTextField.objects.get(parent_item=item_instance,\
						field_name=field_entry)
				elif field_type == 'float':
					to_change = CustomFloatTextField.objects.get(parent_item=item_instance,\
						field_name=field_entry)
				to_change.field_value = data[field];
				to_change.save();
			# perhaps the data is currently null (no entry in custom table)
			except ObjectDoesNotExist as ex2:
				print("Exception: ")
				print(type(ex2).__name__)
				if field_type == 'st':
					to_change = CustomShortTextField.objects.create(parent_item=item_instance,\
						field_name=field_entry, field_value = data[field])
				elif field_type == 'lt':
					to_change = CustomLongTextField.objects.get(parent_item=item_instance,\
						field_name=field_entry, field_value = data[field])
				elif field_type == 'int':
					to_change = CustomIntTextField.objects.get(parent_item=item_instance,\
						field_name=field_entry, field_value = data[field])
				elif field_type == 'float':
					to_change = CustomFloatTextField.objects.get(parent_item=item_instance,\
						field_name=field_entry, field_value = data[field])
				to_change.save();


	item_instance.save();



def modify_an_item(request, item_id):
	itemToChange = get_object_or_404(Item, pk=item_id);
	ItemForm = ItemForm_factory();

	# on a post we (print) the data and then return success
	if request.method == 'POST':
		item_form = ItemForm(request.POST);
		if item_form.is_valid():
			updateItem(itemToChange, item_form.cleaned_data);
			for key in item_form.cleaned_data.keys():
				print('key: ' + key)
				print('data: ' + str(item_form.cleaned_data[key]))
			return HttpResponseRedirect('/manager/update_success');

	# otherwise, it's a GET, and we init the form using the current data
	else:
		item_dict = item_to_dict(itemToChange);
		item_form = ItemForm(item_dict);

	#item_form = ItemForm(item_dict);
	#item_form=ItemForm();
	
	#print(item_to_dict(itemToChange));
	context = {
		'item_form': item_form,
	}
	return render(request, 'manager/modify_an_item.html', context);

def update_success(request):
	return render(request, 'manager/update_success.html');

def item_to_dict(item_instance):
	item_dict = dict();

	for field in item_instance._meta.get_fields():
		# Okay this is popsicle sticks held together with funtac;
		# the db has lingering old fields, which don't exist with
		# getattr.  Additionally, the 'id' field will not be part
		# of the form, so it will (I think) yell at me when I try
		# to use this dictionary to populate the form.
		# Also tags... it's some strange RelatableManager or something
		# which won't be parsed correctly by the form.
		if not (field.name == 'id' or field.name == 'tags'):
			try:
				item_dict[field.name] = getattr(item_instance, field.name);
			except AttributeError:
				pass; #fml

	item_tags = Tag.objects.filter(item_id=item_instance);

	# now we add the tags by hand because... we have to
	tag_list = [];
	for tag in item_tags:
		tag_list.append(tag.pk);
	item_dict['tags'] = tag_list;

	print('item dict: ');
	print(item_dict);
	return item_dict;