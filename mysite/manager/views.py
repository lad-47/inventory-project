from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from datetime import date
from django.contrib.auth.models import User
from home.models import *
from .forms import ServiceForm_factory, ItemForm_factory, AssetForm_factory, TagCreateForm, TagModifyForm, TagDeleteForm, \
PositiveIntArgMaxForm
from .auto_increment import generateAssetTag
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from urllib import parse
from django.db import IntegrityError
from rest_framework import status
from home.models import SubscribedEmail,EmailBody,EmailTag,LoanDate
from django.core.mail import EmailMessage
from django.core.files.storage import FileSystemStorage
from manager.auto_increment import generateAssetTag
#from jinja2.compiler import generate

def manager_home(request):
	return render(request, 'manager/manager_home.html');

def cart_requests(request):
	#check if the user is a manager
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	#this duplicated code is necessary (I think) because of the
	#restrictive nature of calling things from a template
	cart_requests = Cart_Request.objects.exclude(cart_status='P');
	cart_requestsO = cart_requests.filter(cart_status='O');
	cart_requestsO_and_v = create_request_info(cart_requestsO);

	all_reqs = Request.objects.all()
	loans = all_reqs.filter(status='L')
	backfills = all_reqs.filter(status='B')
	cart_requestsL = set()
	cart_requestsB = set()
	for subreq in loans:
		cart_requestsL.add(subreq.parent_cart)
	for subreq in backfills:
		cart_requestsB.add(subreq.parent_cart)
		
	cart_requestsL_and_v = create_request_info(cart_requestsL);
	cart_requestsB_and_v = create_request_info(cart_requestsB);

	context = {
		'outstanding': cart_requestsO_and_v,
		'loans': cart_requestsL_and_v,
		'backfills':cart_requestsB_and_v
	}
	return render(request, 'manager/cart_requestsI.html', context)

def request_history(request):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	cart_requests = Cart_Request.objects.all();
	cart_requestsA = cart_requests.filter(cart_status='A')
	cart_requestsL = cart_requests.filter(cart_status='L')
	cart_requestsD = cart_requests.filter(cart_status='D');
	cart_requestsA_and_v = create_request_info(cart_requestsA);
	cart_requestsD_and_v = create_request_info(cart_requestsD);
	cart_requestsL_and_v = create_request_info(cart_requestsL);
	context = {
		'approved': cart_requestsA_and_v,
		'denied': cart_requestsD_and_v,
		'loaned': cart_requestsL_and_v,
	}
	return render(request, 'manager/request_history.html', context);


def create_request_info(cart_requests):
	cart_requests_and_v = [];
	for cart_request in cart_requests:
		subrequests = Request.objects.filter(parent_cart=cart_request);
		valid = True;
		for subrequest in subrequests:
			itemToChange = subrequest.item_id
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
	req_info = []
	i=0
	for subrequest in subrequests:
		itemToChange = subrequest.item_id
		oldQuantity = itemToChange.count;
		requestAmount = subrequest.quantity;
		newQuantity = oldQuantity - requestAmount;
		valid = not (newQuantity < 0)
		req_info+=[(subrequest, requestAmount, oldQuantity, valid, itemToChange, subrequest.status)];
		if subrequest.status=='B' or subrequest.suggestion=='B':
			req_info[i]+= (FileSystemStorage().url(BackfillPDF.objects.filter(request=subrequest)[0].pdf),)
		i+=1
	return req_info;


def cart_request_details(request, cart_request_id):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')

	current_request = get_object_or_404(Cart_Request, pk=cart_request_id);
	if not current_request.cart_status == 'O':
		return render(request, 'home/message.html', {'message':'Request Not Outstanding'})
	subrequests = Request.objects.filter(parent_cart_id=cart_request_id);

	#assemble useful info to pass to template or use for db manipulation
	req_info = create_indv_request_info(current_request);
	##handle the data from the form on a post
	if request.method == 'POST':
		ServiceForm = ServiceForm_factory(current_request);
		service_form = ServiceForm(request.POST);
		if service_form.is_valid():
			message = 'Your request for:\n'
			tag=EmailTag.objects.all()[0].tag
			new_status = service_form.cleaned_data['approve_deny'];
			if new_status == 'A' or new_status == 'L' or new_status == 'B':
				current_request.cart_status=new_status;
				current_request.suggestion='D'
				for el in req_info:
					if not el[3]:
						#this is a place I could fix things
						return HttpResponseRedirect('/manager/request_failure');
				for el in req_info:
					if el[0].item_id.is_asset:
						assetPKs_used = list();
						for i in range(0, el[0].quantity):
							key = el[4].item_name+'_'+str(i+1);
							assetPK = service_form.cleaned_data[key];
							if assetPK in assetPKs_used:
								return render(request, 'manager/success.html', {'message': 'Cannot assign the same asset twice.'})
							assetPKs_used.append(assetPK);
						for i in range(0, el[0].quantity):
							key = el[4].item_name+'_'+str(i+1);
							assetPK = service_form.cleaned_data[key];
							if not assetPK:
								return render(request, 'manager/success.html', {'message':'Did not assign assets.'});
							asset = Asset.objects.get(pk=assetPK);
							new_req = Request.objects.create(owner=el[0].owner, item_id=asset, \
								reason=el[0].reason, admin_comment=el[0].admin_comment, quantity=1, \
								status=new_status, suggestion='D',\
								parent_cart=el[0].parent_cart)
						el[0].delete();
					else:
						el[4].count = el[2]-el[1]; ##update item quantity
						update_assets(item_name=el[4].item_name);
						message+=el[0].item_id.item_name+' x'+str(el[0].quantity)+"\n"
						el[0].status=new_status; ##subrequest was serviced
						el[0].admin_comment=service_form.cleaned_data['admin_comment'];
						el[0].suggestion='D'
						el[0].save();  ##save the subrequest's updated status
						el[4].save();  ##save the item with new quantity
				message+='has been APPROVED'
				tag+=' Request APPROVED'
			else:
				current_request.cart_status='D';
				current_request.suggestion='D'
				for el in req_info:
					el[0].status='D'; ##subrequest was serviced
					el[0].admin_comment=service_form.cleaned_data['admin_comment'];
					el[0].suggestion='D'
					message+=el[0].item_id.item_name+' x'+str(el[0].quantity)+"\n"
					el[0].save();
				message+='has been DENIED'
				tag+=' Request DENIED'
			current_request.cart_admin_comment=service_form.cleaned_data['admin_comment'];
			current_request.save();
			email = EmailMessage(
				tag,
				message,
				'from@example.com',
				[current_request.cart_owner.email]
			)
			email.send()
			return HttpResponseRedirect('/manager/request_success');

	##the form that will be sent to the template on a GET
	else:
		ServiceForm = ServiceForm_factory(current_request);
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

	print(req_info)
	context = {
		'current_request': current_request,
		'req_info': req_info,
	}
	return render(request, 'manager/old_cart_request_details.html', context);



def logs(request, *args, **kwargs):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	logs = Log.objects.all().order_by('-timestamp')
	items = Item.objects.all()
	users = User.objects.all()
	page = request.GET.get('page', 1)
	new_request = request.GET.copy()
	if 'page' in new_request.keys():
		del new_request['page']
	params = parse.urlencode(new_request)
	if request.method == 'GET':  # If the form is submitted
		item_query = request.GET.get('item_box', None)
		user_query = request.GET.get('user_box', None)
		time_query = request.GET.get('date', None)
		if item_query is not None and not item_query=="":
			try:
				item = Item.objects.get(item_name=item_query)
				logs = logs.filter(involved_item=item.id)
			except Item.DoesNotExist:
				paginator = Paginator(logs, 10)
				logs = paginator.page(1)
				new_request['item_box']=''
				new_request['user_box']=''
				params = parse.urlencode(new_request)
				context = {
					'logs': logs,
					'items': items,
					'users': users,
					'params': params,
					'error': "Item does not exist" }
				return render(request, 'manager/logs.html', context)
		if user_query is not None and not user_query=="":
			try:
				user = User.objects.get(username=user_query)
				logs = logs.filter(initiating_user=user.id)
			except User.DoesNotExist:
				paginator = Paginator(logs, 10)
				logs = paginator.page(1)
				new_request['user_box']=''
				params = parse.urlencode(new_request)
				context = {
					'logs': logs,
					'items': items,
					'users': users,
					'params': params,
					'error': "User does not exist" }
				return render(request, 'manager/logs.html', context)
		if time_query is not None and not time_query=="":
			date_string = time_query.split("-")
			logs = logs.filter(timestamp__date__gte=date(int(date_string[0]),int(date_string[1]),int(date_string[2])))
	paginator = Paginator(logs, 10)
	try:
		logs = paginator.page(page)
	except PageNotAnInteger:
		logs = paginator.page(1)
	except EmptyPage:
		logs = paginator.page(paginator.num_pages)
	context = {
		'logs': logs,
		'items': items,
		'users': users,
		'params': params
	}
	return render(request, 'manager/logs.html', context)


def updateItem(item_instance, data):
	for field in data.keys():
		item_instance.name_unique_check = data['item_name']
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

		# AttributeError should mean it's a custom field
		# I have no idea why it throws ValueError for customs...
		except AttributeError as ex:
			change_cf(item_instance, field, data[field]);

	item_instance.save();

def change_cf(item_instance, field, new_data):
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
			to_change = CustomIntField.objects.get(parent_item=item_instance,\
				field_name=field_entry)
		elif field_type == 'float':
			to_change = CustomFloatField.objects.get(parent_item=item_instance,\
				field_name=field_entry)
		else:
			raise ValueError("Field type not st, lt, int, or float");
		print("old value")
		print(to_change.field_value)
		to_change.field_value = new_data;
		print("new value")
		print(to_change.field_value)
		to_change.save();
	# perhaps the data is currently null (no entry in custom table)
	except ObjectDoesNotExist as ex2:
		print("Exception: ")
		print(type(ex2).__name__)
		if field_type == 'st' and not new_data=="":
			to_change = CustomShortTextField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = new_data)
			to_change.save();
		elif field_type == 'lt' and not new_data=="":
			to_change = CustomLongTextField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = new_data)
			to_change.save();
		elif field_type == 'int' and new_data is not None:
			to_change = CustomIntField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = new_data)
			to_change.save();
		elif field_type == 'float' and new_data is not None:
			to_change = CustomFloatField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = new_data)
			to_change.save();to_change.save();

def modify_an_item(request, item_id):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	itemToChange = get_object_or_404(Item, pk=item_id);
	ItemForm = ItemForm_factory(is_asset_row=itemToChange.is_asset);

	# on a post we (print) the data and then return success
	if request.method == 'POST':
		item_form = ItemForm(request.POST);
		if item_form.is_valid():
			action = "/manager/modify_an_item_action/"+str(item_id) + "/";
			message="Modification of this item will change it in the database.";
			context = {
				'form':item_form,
				'action':action,
				'message':message,
				'submit_button':"Yes, Update Item",

			}
			return render(request, 'manager/confirmation.html', context)
			try:
				updateItem(itemToChange, item_form.cleaned_data);
			except IntegrityError:
				return render(request, 'manager/success.html', {'message':'Item with that name exists.'})
			#for key in item_form.cleaned_data.keys():
				#print('key: ' + key)
				#print('data: ' + str(item_form.cleaned_data[key]))
			#return HttpResponseRedirect('/manager/update_success');

	# otherwise, it's a GET, and we init the form using the current data
	else:
		item_dict = item_to_dict(itemToChange);
		item_form = ItemForm(item_dict);
# 		item_form.fields['new']=item_form.fields.get('item_name')
# 		print(item_form.fields.get('item_name'))
# 		print(item_form.data)

	#item_form = ItemForm(item_dict);
	#item_form=ItemForm();

	#print(item_to_dict(itemToChange));
	context = {
		'item_form': item_form,
		'is_asset': False,
	}
	return render(request, 'manager/modify_an_item.html', context);

def modify_an_item_action(request, item_id):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	itemToChange = get_object_or_404(Item, pk=item_id);
	ItemForm = ItemForm_factory(is_asset_row=itemToChange.is_asset);
	if request.method == 'POST':
		item_form = ItemForm(request.POST);
		if item_form.is_valid():
			convertCheck = False;
			if 'convert' in item_form.cleaned_data.keys():
				convertCheck = item_form.cleaned_data.pop('convert')
			try:
				updateItem(itemToChange, item_form.cleaned_data);
			except IntegrityError:
				return render(request, 'manager/success.html', {'message':'Item with that name exists.'})
			if convertCheck  and itemToChange.is_asset:
				convert_asset_to_item(itemToChange);
			elif convertCheck  and not itemToChange.is_asset:
				convert_item_to_asset(itemToChange);
			return HttpResponseRedirect('/manager/update_success');
		else:
			context = {
				'item_form:':item_form,
				'is_asset': False,
				}
			return render(request, 'manager/modify_an_item.html', context)

	# we should never get here with a GET
	# if we do, just render the home page
	render(request, 'index.html');

def convert_item_to_asset(item):
	itemQuantity = item.count;
	item.is_asset = True;
	item.save();
	cfs = CustomFieldEntry.objects.filter(per_asset=True)
	for cf in cfs:
		try:
			kind = cf.value_type
			if kind == 'st':
				a = CustomShortTextField.objects.get(parent_item=item, field_name=cf)
				a.delete()
			if kind == 'lt':
				a = CustomLongTextField.objects.get(parent_item=item, field_name=cf)
				a.delete()
			if kind == 'int':
				a = CustomIntField.objects.get(parent_item=item, field_name=cf)
				a.delete()
			if kind == 'float':
				a = CustomFloatField.objects.get(parent_item=item, field_name=cf)
				a.delete()
		except Exception:
			pass

	for x in range (0, itemQuantity):
		newAsset = Asset.objects.create(item_name=item.item_name, count=1, model_number=item.model_number, description=item.description, is_asset = True, asset_tag = generateAssetTag())
	requests = Request.objects.filter(item_id=item).exclude(status='O').exclude(status='A').exclude(status='D').exclude(status='P').exclude(status='R').exclude(status='Z')
	for request in requests:
		is_pdf = False
		try:
			pdf = BackfillPDF.objects.get(request=request)
			is_pdf = True
		except BackfillPDF.DoesNotExist:
			pass
		for x in range(0,request.quantity):
			newAsset = Asset.objects.create(item_name=item.item_name, count=0, model_number=item.model_number, description=item.description, is_asset = True, asset_tag = generateAssetTag())
			newreq = Request.objects.create(owner = request.owner,item_id = newAsset,reason = request.reason,admin_comment = request.admin_comment,quantity = 1,status = request.status,suggestion = request.suggestion,parent_cart = request.parent_cart)
			if is_pdf:
				BackfillPDF.objects.create(request=newreq,pdf=pdf.pdf)
	for request in requests:
		request.delete()
	return True;

def convert_asset_to_item(asset):
	assets = Asset.objects.filter(item_name=asset.item_name);
	asset.count = len(assets);
	asset.is_asset = False;
	asset.save();
	for asset in assets:
		asset.delete();
	return True;

def modify_an_asset(request, asset_id, conf):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	asset = get_object_or_404(Asset, pk=asset_id);
	AssetForm = AssetForm_factory(asset.asset_tag, (not request.user.is_superuser));
	asset_form = AssetForm(asset_to_dict(asset));
	print(asset_to_dict(asset));
	# on a post we (print) the data and then return success
	if (request.method=='POST' and conf=='0'):
		print("in post 0")
		print(request.POST);
		asset_form = AssetForm(request.POST);
		if asset_form.is_valid():
			action = "/manager/modify_an_asset/"+str(asset_id) + "/1/";
			message="Modification of this asset will change it in the database.";
			context = {
				'form':asset_form,
				'action':action,
				'message':message,
				'submit_button':"Yes, Update Asset",
			}
			return render(request, 'manager/confirmation.html', context)
	elif request.method == 'POST' and conf=='1':
			asset_form = AssetForm(request.POST);
			if asset_form.is_valid():
				print(asset_form.cleaned_data);
				try:
					updateAsset(asset, asset_form.cleaned_data);
				except IntegrityError:
					return render(request, 'home/message.html',{'message':'Asset Tag Exists.'})
			return HttpResponseRedirect('/manager/asset_update_success');


	context = {
		'item_form':asset_form,
		'is_asset': True,
	}
	print("before get (or invalid) render")
	print(asset_form.is_valid());
	print(conf);
	return render(request, 'manager/modify_an_item.html', context);

def updateAsset(asset, data):
	asset.asset_tag = data['asset_tag'];
	asset.save();
	for field in data.keys():
		try:
			cf_entry = CustomFieldEntry.objects.get(field_name=field);
		except CustomFieldEntry.DoesNotExist:
			cf_entry = None; #no data provided for this field or field doesn't exist
		if cf_entry:
			print("in change_cf");
			print(field);
			print(data[field])
			change_cf(asset, field, data[field]);


def asset_update_success(request):
	return render(request, 'manager/success.html', {'message':'Asset Modification Successful.'})

def update_success(request):
	return render(request, 'manager/update_success.html');

def asset_to_dict(item_instance):
	item_dict = dict();
	item_dict['asset_tag'] = item_instance.asset_tag;
	custom_fields = CustomFieldEntry.objects.filter(per_asset=True);
	for cf in custom_fields:
		field_type = cf.value_type;
		try:
			if field_type == 'st':
				data_field = CustomShortTextField.objects.get(parent_item=item_instance, field_name=cf);
			elif field_type == 'lt':
				data_field = CustomLongTextField.objects.get(parent_item=item_instance,field_name=cf);
			elif field_type == 'int':
				data_field = CustomIntField.objects.get(parent_item=item_instance,field_name=cf);
			elif field_type == 'float':
				data_field = CustomFloatField.objects.get(parent_item=item_instance,field_name=cf);
			item_dict[cf.field_name] = data_field.field_value;
		except ObjectDoesNotExist:
			pass; # no need to do anything to the dictionary
	return item_dict;

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
				data_field = CustomIntField.objects.get(parent_item=item_instance,field_name=cf);
			elif field_type == 'float':
				data_field = CustomFloatField.objects.get(parent_item=item_instance,field_name=cf);
			item_dict[cf.field_name] = data_field.field_value;
		except ObjectDoesNotExist:
			pass; # no need to do anything to the dictionary
	print('item dict: ');
	print(item_dict);
	return item_dict;

def add_an_item(request):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	ItemForm = ItemForm_factory(is_asset_row=False,is_new_item=True);

	# on a post we (print) the data and then return success
	if request.method == 'POST':
		item_form = ItemForm(request.POST);
		if item_form.is_valid():
			d = item_form.cleaned_data
			d['tags'] = request.POST.getlist('addTags[]', [])
			try:
				createItem(d, 'item');
			except IntegrityError:
				return render(request, 'home/message.html',{'message':'An item with that name already exists'})
			return HttpResponseRedirect('/manager/create_success');

	else:
		item_form = ItemForm();

	tags = Tag.objects.all()

	return render(request, 'manager/add_an_item.html', {'item_form':item_form,'tags':tags})

def add_an_asset_row(request):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	ItemForm = ItemForm_factory(is_asset_row=True);

	# on a post we (print) the data and then return success
	if request.method == 'POST':
		item_form = ItemForm(request.POST);
		if item_form.is_valid():
			try:
				d = item_form.cleaned_data;
				d['count'] = 0;
				d['tags'] = request.POST.getlist('addTags[]',None);
				createItem(d, 'asset_row');
			except IntegrityError:
				return render(request, 'home/message.html',{'message':'An item with that name already exists'})
			return HttpResponseRedirect('/manager/create_success');

	else:
		item_form = ItemForm();

	return render(request, 'manager/add_an_item.html', {'item_form':item_form})

def add_an_asset(request, item_id):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	item = get_object_or_404(Item, pk=item_id);

	asset_tag = generateAssetTag();
	AssetForm = AssetForm_factory(asset_tag, False);

	# on a post we (print) the data and then return success
	if request.method == 'POST':
		item_form = AssetForm(request.POST);
		if item_form.is_valid():
			try:
				createAsset(item_form.cleaned_data, item);
				update_assets(asset_tag=asset_tag);
			except IntegrityError:
				return render(request, 'home/message.html',{'message':'Asset Tag Exists.'})
			return HttpResponseRedirect('/manager/create_success');

	else:
		item_form = AssetForm();

	return render(request, 'manager/add_an_item.html', {'item_form':item_form, 'is_asset':True,})


def createItem(data, kind):
	if(kind == 'item'):
		item_instance = Item.objects.create(item_name=data['item_name'], name_unique_check=data['item_name'],\
		 	model_number=data['model_number'], description=data['description'],\
		 	count=data['count'], is_asset=False);
		cfs = CustomFieldEntry.objects.all();
	elif(kind == 'asset_row'):
		item_instance = Item.objects.create(item_name=data['item_name'],name_unique_check=data['item_name'],\
		 	model_number=data['model_number'], description=data['description'],\
		 	count=data['count'], is_asset=True);
		cfs = CustomFieldEntry.objects.filter(per_asset=False);
	elif(kind == 'asset'):
		item_instance = Asset.objects.create(asset_tag=generateAssetTag(), item_name=data['item_name'],\
		 	model_number=data['model_number'], description=data['description'],\
		 	count=data['count'], is_asset=True);
		cfs = CustomFieldEntry.objects.filter(per_asset=True);

	for field_entry in cfs:
		field_type = field_entry.value_type;
		field = field_entry.field_name;
		if field_type == 'st' and not data[field]=="":
			to_change = CustomShortTextField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = data[field])
			to_change.save();
		elif field_type == 'lt' and not data[field]=="":
			to_change = CustomLongTextField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = data[field])
			to_change.save();
		elif field_type == 'int' and data[field] is not None:
			to_change = CustomIntField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = data[field])
			to_change.save();
		elif field_type == 'float' and data[field] is not None:
			to_change = CustomFloatField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = data[field])
			to_change.save();

	for tag in data['tags']:
		try:
			item_instance.tags.add(Tag.objects.get(tag=tag));
		except Tag.DoesNotExist:
			pass;
	item_instance.save();

def createAsset(data, item):
	item_instance = Asset.objects.create(asset_tag=data['asset_tag'],\
				item_name=item.item_name, count=1, model_number=item.model_number, is_asset=True,
				description=item.description);

	for tag in item.tags.all():
		item_instance.tags.add(tag);

	item_instance.save();
	cfs = CustomFieldEntry.objects.filter(per_asset=True);

	for field_entry in cfs:
		field_type = field_entry.value_type;
		field = field_entry.field_name;
		if field_type == 'st' and not data[field]=="":
			to_change = CustomShortTextField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = data[field])
			to_change.save();
		elif field_type == 'lt' and not data[field]=="":
			to_change = CustomLongTextField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = data[field])
			to_change.save();
		elif field_type == 'int' and data[field] is not None:
			to_change = CustomIntField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = data[field])
			to_change.save();
		elif field_type == 'float' and data[field] is not None:
			to_change = CustomFloatField.objects.create(parent_item=item_instance,\
				field_name=field_entry, field_value = data[field])
			to_change.save();

def create_success(request):
	return render(request, 'manager/create_success.html');

def tag_handler(request):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')

	# on a POST, these definitions will be overwritten before rendering
	#create_form = TagCreateForm(); --- deprecated
	modify_form = TagModifyForm();
	#delete_form = TagDeleteForm(); --- deprecated

	tags = Tag.objects.all()
	items = Item.objects.all()

	context = {
		#'create_form': create_form,
		'modify_form': modify_form,
		#'delete_form': delete_form,
		'tags': tags,
		'items': items
	}

	return render(request, 'manager/tag_handler.html', context);

def create_tag(request):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	if request.method == 'POST':
		try:
			tag_name = request.POST.get('new_tag_name', None)
			print("Tag Name: "+str(tag_name))
			new_tag = Tag.objects.create(tag=tag_name)
		except IntegrityError:
			context = {
				#'create_form': create_form,
				'modify_form': TagModifyForm(),
				'delete_form': TagDeleteForm()
			}
			return render(request, 'manager/tag_exists.html', context)

		new_tag.save()
		items = request.POST.getlist('tagExisting[]', [])
		for item in items:
			if item != "":
				item_instance = Item.objects.get(item_name=item)
				item_instance.tags.add(new_tag)
				item_instance.save()
		return HttpResponseRedirect('/manager/tag_success')
		"""
		create_form = TagCreateForm(request.POST);
		if create_form.is_valid():
			try:
				newTag = Tag.objects.create(\
					tag=create_form.cleaned_data['new_tag_name']);
			except IntegrityError:
				context = {
					'create_form': create_form,
					'modify_form': TagModifyForm(),
					'delete_form': TagDeleteForm(),
					}
				return render(request, 'manager/tag_exists.html', context);

			newTag.save();
			for itemPK in create_form.cleaned_data['tagged_items']:
				item = Item.objects.get(pk=itemPK);
				item.tags.add(newTag);
				item.save();
			return HttpResponseRedirect('/manager/tag_success');
	else:
		create_form = TagCreateForm();"""
	modify_form = TagModifyForm();
	delete_form = TagDeleteForm();

	context = {
		'create_form': create_form,
		'modify_form': modify_form,
		'delete_form': delete_form,
	}

	return render(request, 'manager/tag_handler.html', context);


def modify_tag(request):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	if request.method=='POST':
		modify_form = TagModifyForm(request.POST);
		if modify_form.is_valid():
			try:
				tagToUpdate = Tag.objects.get(\
					tag=modify_form.cleaned_data['old_name']);
				tagToUpdate.tag = modify_form.cleaned_data['new_name'];
				tagToUpdate.save();
			except Tag.DoesNotExist:
				return render(request, 'manager/success.html', {'message':"Tag does not exist in database."})
			except IntegrityError:
				context = {
					'create_form': TagCreateForm(),
					'modify_form': modify_form,
					'delete_form': TagDeleteForm(),
					}
				return render(request, 'manager/tag_exists.html', context);
			return HttpResponseRedirect('/manager/tag_success');

	else:
		modify_form = TagModifyForm();
	create_form = TagCreateForm();
	delete_form = TagDeleteForm();

	context = {
		'create_form': create_form,
		'modify_form': modify_form,
		'delete_form': delete_form,
	}

	return render(request, 'manager/tag_handler.html', context);

# deprecated
def delete_tag_conf(request):

	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	if request.method=='POST':
		delete_form = TagDeleteForm(request.POST);
		if delete_form.is_valid():
			create_form = TagCreateForm();
			modify_form = TagModifyForm();
			context = {
				'form': delete_form,
				'message':"Are you sure you want to delete these tags?",
				'submit_button':"Yes, Delete Tags",
				'action':'/manager/tag_handler/delete_2/',

				}
			return render(request, 'manager/confirmation.html', context);
	else:
		delete_form = TagDeleteForm();
	create_form = TagCreateForm();
	modify_form = TagModifyForm();

	context = {
		'create_form': create_form,
		'modify_form': modify_form,
		'delete_form': delete_form,
	}

	return render(request, 'manager/tag_handler.html', context);

def delete_tag_action(request):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	if request.method=='POST':
		delete_tags = request.POST.getlist('deleteTags[]', [])
		if delete_tags is not None:
			for tag in delete_tags:
				try:
					tag_instance = Tag.objects.get(tag=tag)
					tag_instance.delete()
				except:
					# User entered a nonexistent tag, or tag was not able to be deleted
					pass
			return HttpResponseRedirect('/manager/tag_success')
		""" deprecated form code:
		delete_form = TagDeleteForm(request.POST);
		if delete_form.is_valid():
			for tagPK in delete_form.cleaned_data['to_delete']:
				tag = Tag.objects.get(pk=tagPK);
				tag.delete();
			return HttpResponseRedirect('/manager/tag_success');
	else:
		delete_form = TagDeleteForm();"""
	create_form = TagCreateForm();
	modify_form = TagModifyForm();

	context = {
		'create_form': create_form,
		'modify_form': modify_form#,
		#'delete_form': delete_form,
	}

	return render(request, 'manager/tag_handler.html', context);


def tag_delete_success(request):
	return render('manager/tag_success.html');

def tag_success(request):
	return render (request, 'manager/tag_success.html');

def direct_disburse(request):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')

	items = Item.objects.all()
	users = User.objects.all()
	# on a post we (print) the data and then return success
	if request.method == 'POST':
		items_set = request.POST.getlist('myItems[]',None)
		count_set = request.POST.getlist('myCounts[]',None)
		type = request.POST.get('select','Disburse')
		user = request.POST.get('user',None)
		owner=User.objects.get(username=user)
		comment = request.POST.get('comment',None)
		info=''
		if type=='Disburse':
			info='direct disbursement'
		else:
			info='direct loan'
		cart = Cart_Request(cart_status='O',cart_reason=info,cart_admin_comment=comment,cart_owner=owner)
		cart.save()
		for i in range(0,len(items_set)):
			if items_set[i]!='':
				try:
					item = Item.objects.get(item_name=items_set[i])
					if item.count<int(count_set[i]):
						reqs = Request.objects.filter(parent_cart=cart)
						for req in reqs:
							req.delete()
						cart.delete()
						context = {
							'items': items,
							'users': users,
							'error': 'Insufficient quantity of '+item.item_name
						}
						return render(request, 'manager/direct_disburse.html', context)
					item_request=Request(status='O',reason=info,item_id=item,owner=owner,admin_comment=comment,quantity=int(count_set[i]),parent_cart=cart)
					item_request.save()
				except Item.DoesNotExist:
					context = {
						'items': items,
						'users': users,
						'error': 'Invalid item name entered: '+items_set[i]
					}
					return render(request, 'manager/direct_disburse.html', context)
		#cart.save()
		subrequests = Request.objects.filter(parent_cart=cart);
		letter="A"
		word="disbursed"
		if type=='Loan':
			letter="L"
			word="loaned"
		cart.cart_status=letter
		message = 'You have been directly '+word+':\n'
		for subrequest in subrequests:
			itemToChange = Item.objects.get(id=subrequest.item_id_id);
			newQuantity = itemToChange.count - subrequest.quantity;
			itemToChange.count = newQuantity
			subrequest.status=letter
			subrequest.save()
			message+=subrequest.item_id.item_name+' x'+str(subrequest.quantity)+"\n"
			itemToChange.save()
		cart.save()
		tag=EmailTag.objects.all()[0].tag
		email = EmailMessage(
			tag+' Direct Disburse',
			message,
			'from@example.com',
			[owner.email]
		)
		email.send()

		if type=='Disburse':
			return HttpResponseRedirect('/manager/disburse_success/Disbursed');
		else:
			return HttpResponseRedirect('/manager/disburse_success/Loaned');

	context = {
		'items': items,
		'users': users
		}
	return render(request, 'manager/direct_disburse.html', context)

def disburse_success(request, message):
	return render(request, 'manager/success.html', {'message': message})


def handle_loan(request, request_id, new_status):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	req = get_object_or_404(Request, pk=request_id);
	is_pdf = False
	try:
		pdf = BackfillPDF.objects.get(request=req)
		is_pdf = True
	except BackfillPDF.DoesNotExist:
		pass
	old_status = req.status
	parent = req.parent_cart;
	quantity = req.quantity;

	# will be used to null out per_asset cf's later
	try:
		a = req.item_id.asset
		backfill_return = (req.status == 'B' and new_status == 'R')
	except Asset.DoesNotExist:
		backfill_return = False;
	print(backfill_return);


	if request.method == 'POST':
		form = PositiveIntArgMaxForm(request.POST, max_val=quantity);
		if form.is_valid():
			to_new_status = form.cleaned_data['Amount'];
			print(to_new_status)
			no_longer_loaned = to_new_status
			comment = form.cleaned_data['Comment'];

			if (quantity-to_new_status < 0):
				return render(request, 'manager/success.html', {'message': 'Failure.'})

			signal_logs = Request.objects.create(owner=req.owner, status='Z',\
			quantity=(quantity-to_new_status), item_id=req.item_id, parent_cart=req.parent_cart,\
			reason=req.reason, admin_comment=comment);
			signal_logs.delete();
			#still_old_status = Request.objects.create(owner=req.owner, status=req.status, \
			#quantity=(quantity-no_longer_loaned), item_id=req.item_id, parent_cart=req.parent_cart,\
			#reason=req.reason, admin_comment=comment);
			#still_old_status.save();
			

			new_request = Request.objects.create(owner=req.owner, status=new_status,\
			quantity=(to_new_status), item_id=req.item_id, parent_cart=req.parent_cart, \
			reason=req.reason, admin_comment=comment);
			#disbursed.save(); .create already saves
			if is_pdf:
				BackfillPDF.objects.create(request=new_request,pdf=pdf.pdf)
			tag=EmailTag.objects.all()[0].tag
			message=""

			if new_status == 'A':
				message = "You have been disbursed "+str(to_new_status)+" x "+str(req.item_id)+" from your previous loan"
				tag += " Disbursement"
			elif new_status == 'R':
				message = "You have returned "+str(to_new_status)+" x "+str(req.item_id)
				tag += " Loan Returned"
			elif new_status == 'L':
				message = "Now on loan to you: "+str(to_new_status)+" x "+str(req.item_id)
				tag += "Backfill now loaned" # maybe "backfill rejected"?
			elif new_status == 'B':
				message = "Marked for backfill: "+str(to_new_status)+" x "+str(req.item_id)
				tag += "Marked for Backfill"
			else:
				message = "error"
				tag += "error"

			email = EmailMessage(
				tag,
				message,
				'from@example.com',
				[req.owner.email]
			)
			email.send()
			# have active and outstanding requests
			# active = backfill or loans
			if new_status == 'R':
				involved_item = req.item_id;
				print(involved_item.count)
				involved_item.count = involved_item.count + no_longer_loaned;
				print(involved_item.count)
				involved_item.save();
				update_assets(item_name=involved_item.item_name);

			if backfill_return:
				asset = req.item_id;
				cfs = CustomFieldEntry.objects.filter(per_asset=True);
				for cf in cfs:
					kind = cf.value_type;
					if kind == 'st':
						a = CustomShortTextField.objects.get(parent_item=asset, field_name=cf);
					elif kind == 'lt':
						a = CustomLongTextField.objects.get(parent_item=asset, field_name=cf);
					elif kind == 'int':
						a = CustomIntField.objects.get(parent_item=asset, field_name=cf);
					elif kind == 'float':
						a = CustomFloatField.objects.get(parent_item=asset, field_name=cf);
					else:
						raise ValueError('value_type wasnt st, lt, int, or float');
					a.field_value = None;
					a.save();



			req.quantity = quantity - to_new_status;
			if(req.quantity > 0):
				req.save();
			else:
				req.delete();
			
			still_loaned = False;
			for subreq in Request.objects.filter(parent_cart = parent):
				if subreq.status == 'L' or subreq.status == 'B':
					still_loaned = True;
			if not still_loaned:
				parent.cart_status = 'A';
				parent.save();
			
			if parent.suggestion == 'B':	
				children = Request.objects.filter(parent_cart=parent)
				still_suggest = False
				for child in children:
					if child.suggestion=='B':
						still_suggest = True
				if not still_suggest:
					parent.suggestion='D'
					parent.save()

			return HttpResponseRedirect('/manager/loan_handle_success');


	else:
		form = PositiveIntArgMaxForm(max_val=quantity);

	if new_status == 'A':
		heading = "Disbursing";
		button = "Disburse";
	elif new_status == 'R' and old_status == 'B':
		heading = "Backfilling";
		button = "Mark Backfill as Satisfied";
	elif new_status == 'R':
		heading = "Returning";
		button = "Mark as Returned";
	elif new_status == 'B':
		heading = "For Backfill";
		button = "Mark for Backfill";
	elif new_status == 'L':
		heading = "To Loan";
		button = "Mark as Loaned";

	context = {
		'form': form,
		'item': req.item_id,
		'loaned': quantity,
		'heading': heading,
		'button':button,
	}
	return render(request, 'manager/disburse_loaned.html', context)

def disburse_loaned(request, request_id):
	return handle_loan(request, request_id, 'A');

def return_loaned(request, request_id):
	return handle_loan(request, request_id, 'R');

def convert_status(request, request_id, new_status):
	return handle_loan(request, reqeust_id, new_status);

def loan_handle_success(request):
	return render(request, 'manager/success.html', {'message': 'Loan Status Updated.'})

def loan_backfill_handler(request, status_type):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	request_list = Request.objects.all().filter(status=status_type);

	# it's a search
	if request.method == 'GET':
		search_user = request.GET.get('user_box', None)
		search_item = request.GET.get('item_box', None)

		if search_user:
			try:
				user = User.objects.get(username=search_user);
				request_list = request_list.filter(owner=user);
			except User.DoesNotExist:
				request_list = None;

		if search_item:
			try:
				item = Item.objects.get(item_name=search_item);
				request_list = request_list.filter(item_id=item);
			except Item.DoesNotExist:
				request_list = None;

	items = Item.objects.all();
	users = User.objects.all();
	context = {
		'request_list': request_list,
		'items':items,
		'users':users,
		'loan': (status_type == 'L'),

	}
	return render(request, 'manager/loan_handler.html',context)

def loan_handler(request):
	return loan_backfill_handler(request, 'L');

def backfill_handler(request):
	return loan_backfill_handler(request, 'B');

def deny_backfill(request, request_id):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	req = Request.objects.get(id=request_id)
	if req.suggestion == 'B':
		req.suggestion = 'L'
		req.save()
		
	parent = req.parent_cart
	if parent.suggestion == 'B':	
				children = Request.objects.filter(parent_cart=parent)
				still_suggest = False
				for child in children:
					if child.suggestion=='B':
						still_suggest = True
				if not still_suggest:
					parent.suggestion='L'
					parent.save()
	return HttpResponseRedirect('/manager/loan_handler');

def assemble_loan_info(request_list):
	req_info = [];
	for req in request_list:
		involved_item = req.item_id;
	return 0;

# a method to call after doing anything to an asset;
# this will update the count of the row in the item table
# call with either asset_tag or item_name
# ex:  update_assets(asset_tag=1111)  or
#      update_assets(item_name="Resistor")
#      update_assets(check_all=True);
def update_assets(**kwargs):

	if not (kwargs):
		raise ValueError("Neither valid argument (asset_tag or item_name or check_all) was provided");

	if kwargs.get('check_all', False):
		asset_rows = Item.objects.filter(is_asset=True);
		for row in asset_rows:
			num_assets = Asset.objects.filter(item_name=row.item_name, count=1).count();
			row.count = num_assets;
			row.save();
		return;
			
	if kwargs.get('asset_tag', False):
		item_name = Asset.objects.get(asset_tag=kwargs['asset_tag']).item_name;
	else:
		item_name = kwargs['item_name'];

	assets_left = Asset.objects.filter(item_name=item_name, count=1).count();
	asset_item_row = Item.objects.get(item_name=item_name);
	if asset_item_row.is_asset:
		asset_item_row.count = assets_left;
		asset_item_row.save();
