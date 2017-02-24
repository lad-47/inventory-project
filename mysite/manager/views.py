from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from datetime import date
from django.contrib.auth.models import User
from home.models import Request, Cart_Request, User, Item, Log, Tag, CustomFieldEntry, \
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
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
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


def updateItem(item_instance, data):
	for field in data.keys():
		
		# we have to parse the tags by hand
		if field == 'tags':
			for tag in Tag.objects.all():
				item_instance.tags.remove(tag);
			for tagPK in data['tags']: #also data[field]
				item_instance.tags.add(Tag.objects.get(pk=tagPK));
			continue;

		# the getattr is a hacky way of getting it to throw an AttributeError
		try:
			getattr(item_instance, field);
			setattr(item_instance, field, data[field]);
			print("setting: ")
			print(field);

		# AttributeError should mean it's a custom field
		# I have no idea why it throws ValueError for customs...
		except AttributeError as ex:
			field_entry = CustomFieldEntry.objects.get(field_name=field);
			field_type = field_entry.value_type;
			print("inside attribute error")
			try:
				if field_type == 'st':
					print("updating st field")
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
				print("old value")
				print(to_change.field_value)
				to_change.field_value = data[field];
				print("new value")
				print(to_change.field_value)
				to_change.save();
			# perhaps the data is currently null (no entry in custom table)
			except ObjectDoesNotExist as ex2:
				print("Exception: ")
				print(type(ex2).__name__)
				if field_type == 'st':
					to_change = CustomShortTextField.objects.create(parent_item=item_instance,\
						field_name=field_entry, field_value = data[field])
				elif field_type == 'lt':
					to_change = CustomLongTextField.objects.create(parent_item=item_instance,\
						field_name=field_entry, field_value = data[field])
				elif field_type == 'int':
					to_change = CustomIntTextField.objects.create(parent_item=item_instance,\
						field_name=field_entry, field_value = data[field])
				elif field_type == 'float':
					to_change = CustomFloatTextField.objects.create(parent_item=item_instance,\
						field_name=field_entry, field_value = data[field])
				print("to change field name: ")
				print(to_change.field_name);
				to_change.save();


	item_instance.save();



def modify_an_item(request, item_id):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
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

	item_tags = item_instance.tags.all();

	# now we add the tags by hand because... we have to
	tag_list = [];
	for tag in item_tags:
		tag_list.append(tag.pk);
	item_dict['tags'] = tag_list;

	# and finally the custom fields
	custom_fields = CustomFieldEntry.objects.all();
	for cf in custom_fields:
		field_type = cf.value_type;
		try:
			if field_type == 'st':
				data_field = CustomShortTextField.objects.get(parent_item=item_instance, field_name=cf);
			elif field_type == 'lt':
				data_field = CustomLongTextField.objects.get(parent_item=item_instance,field_name=cf);
			elif field_type == 'int':
				data_field = CustomIntTextField.objects.get(parent_item=item_instance,field_name=cf);
			elif field_type == 'float':
				data_field = CustomFloatTextField.objects.get(parent_item=item_instance,ield_name=cf);
			item_dict[cf.field_name] = data_field.field_value;
		except ObjectDoesNotExist:
			pass; # no need to do anything to the dictionary
	print('item dict: ');
	print(item_dict);
	return item_dict;

def add_an_item(request):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	ItemForm = ItemForm_factory();

	# on a post we (print) the data and then return success
	if request.method == 'POST':
		item_form = ItemForm(request.POST);
		if item_form.is_valid():
			createItem(item_form.cleaned_data);
			return HttpResponseRedirect('/manager/create_success');

	else:
		item_form = ItemForm();

	return render(request, 'manager/add_an_item.html', {'item_form':item_form})


def createItem(data):
	item_instance = Item.objects.create(item_name=data['item_name'],\
	 model_number=data['model_number'], description=data['description'],\
	 count=data['count']);

	for field_entry in CustomFieldEntry.objects.all():
		field_type = field_entry.value_type;
		field = field_entry.field_name;
		if field_type == 'st':
			to_change = CustomShortTextField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = data[field])
		elif field_type == 'lt':
			to_change = CustomLongTextField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = data[field])
		elif field_type == 'int':
			to_change = CustomIntTextField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = data[field])
		elif field_type == 'float':
			to_change = CustomFloatTextField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = data[field])
		to_change.save();

	for tagPK in data['tags']:
		item_instance.tags.add(Tag.objects.get(pk=tagPK));
	item_instance.save();

def create_success(request):
	return render(request, 'manager/create_success.html');
