from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Item, Request, Tag, CustomFieldEntry, CustomLongTextField, CustomShortTextField, \
CustomIntField, CustomFloatField, Cart_Request,SubscribedEmail,EmailTag,Asset;
from .forms import CheckoutForm
from .serializers import ItemSerializer
# chance genereic.Listview stuff to ListView
from django.views.generic import View, DetailView, ListView, DeleteView, CreateView, FormView

from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.core.mail import EmailMessage

import os, sys

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def index(request):
	latest_item_list = Item.objects.all()
	tag_list = Tag.objects.distinct('tag')
	if request.method == 'GET':  # If the form is submitted
		latest_item_list = Item.objects.all()
		search_query = request.GET.get('search_box', None)
		model_query = request.GET.get('model_box', None)
		#old_tag_query = request.GET.getlist('select', None)
		#old_extag_query = request.GET.getlist('exselect', None)
		tag_query = request.GET.getlist('myTags[]', None)
		extag_query = request.GET.getlist('exTags[]', None)
		if search_query is not None:
			latest_item_list = latest_item_list.filter(item_name__icontains=search_query)
		if model_query is not None:
			latest_item_list = latest_item_list.filter(model_number__icontains=model_query)
		if tag_query is not None:
			# tags_to_include = []
			for tag in tag_query:
				print(tag)
				# if (tag != ''):
				# 	this_tag = Tag.objects.get(tag=tag)
				# 	tags_to_include.append(this_tag)
				if (tag != ''):
					tag = Tag.objects.get(tag=tag);
					latest_item_list = latest_item_list.filter(tags=tag)
			# if tags_to_include is not None:
			# 	latest_item_list = latest_item_list.filter(tags__in=tags_to_include)
		if extag_query is not None:
			for tag in extag_query:
				if (tag != ''):
					tag = Tag.objects.get(tag=tag)
					latest_item_list = latest_item_list.exclude(tags=tag)
		latest_item_list = sorted(latest_item_list, key=lambda item: item.item_name)
	page = request.GET.get('page', 1)
	paginator = Paginator(latest_item_list, 10)
	try:
		items = paginator.page(page)
	except PageNotAnInteger:
		items = paginator.page(1)
	except EmptyPage:
		items = paginator.page(paginator.num_pages)
	context = {
		'items': items,
		'tag_list': tag_list
	}
	return render(request, 'home/index.html', context)

def detail(request, item_id):
	item = get_object_or_404(Item, pk=item_id)
	tags = item.tags.all()
	if request.user.is_anonymous:
		requests = Request.objects.none()
		
	requests = Request.objects.filter(item_id=item.id, status='O');
	requests = requests | Request.objects.filter(item_id=item.id, status='L')
	requests = requests | Request.objects.filter(item_id=item.id, status='B')
	if item.is_asset:
		assets = Asset.objects.filter(item_name=item.item_name);
	else:
		assets = None;
	if not request.user.is_staff:
		requests = requests.filter(owner=request.user);

	if request.user.is_staff:
		cf_entries = CustomFieldEntry.objects.all();
	else:
		cf_entries = CustomFieldEntry.objects.filter(is_private=False);
	custom_values = get_cfs_from_entries(cf_entries, item);
	context = {
		'item': item,
		'tags': tags,
		'requests': requests,
		'custom': custom_values,
		'user':request.user,
		'assets':assets,
	}
	return render(request, 'home/detail.html', context)


def get_cfs_from_entries(cf_entries, item):
	custom_values = []
	for cf in cf_entries:
		if cf.value_type == 'lt': # Long Text
			try:
				val = CustomLongTextField.objects.get(parent_item=item.id, field_name=cf)
				if val.field_value:
					custom_values.append(val.field_name.field_name+": "+val.field_value)
			except CustomLongTextField.DoesNotExist:
				pass
		elif cf.value_type == 'st': # Short Text
			try:
				val = CustomShortTextField.objects.get(parent_item=item.id, field_name=cf)
				if val.field_value:
					custom_values.append(val.field_name.field_name+": "+val.field_value)
			except CustomShortTextField.DoesNotExist:
				pass
		elif cf.value_type == 'int': # Integer
			try:
				val = CustomIntField.objects.get(parent_item=item.id, field_name=cf)
				if val.field_value:
					custom_values.append(val.field_name.field_name+": "+str(val.field_value))
			except CustomIntField.DoesNotExist:
				pass
		elif cf.value_type == 'float': # Float
			try:
				val = CustomFloatField.objects.get(parent_item=item.id, field_name=cf)
				if val.field_value:
					custom_values.append(val.field_name.field_name+": "+str(val.field_value))
			except CustomFloatField.DoesNotExist:
				pass
	return custom_values;
# asset detail doesn't actauly exist, I forgot Lucas was gonna do this
# I'll leave the code here just in case
def assets_detail(request, item_id):
	item = get_object_or_404(Item, pk=item_id);
	assets = Item.objects.filter(item_name=item.item_name);

	context = {
		'asset_row': item,
		'asset_list': assets,
	}
	return render(request, 'manager/success.html', {'message':"Page Not Implemented"})

def asset_detail(request, asset_id):
	asset = get_object_or_404(Asset, pk=asset_id)
	requests = Request.objects.filter(item_id=asset.id, status='O');
	requests = requests | Request.objects.filter(item_id=asset.id, status='L')
	requests = requests | Request.objects.filter(item_id=asset.id, status='B')
	if request.user.is_staff:
		cf_entries = CustomFieldEntry.objects.filter(per_asset=True);
	else:
		cf_entries = CustomFieldEntry.objects.filter(is_private=False, per_asset=True);

	custom_values = get_cfs_from_entries(cf_entries, asset);
	context = {
		'asset_tag': asset.asset_tag,
		'item': asset,
		'tags': asset.tags.all(),
		'requests': requests,
		'custom': custom_values,
		'user':request.user
	}
	return render(request, 'home/detail.html', context)

def developers(request):
	return render(request, 'home/developers.html')

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
	model = Cart_Request;
	context_object_name = 'request_list';
	template_name = 'home/cart_requests.html';

	def get_queryset(self):
		return Cart_Request.objects.filter(cart_owner=self.request.user).exclude(cart_status='P');

#class serviceRequestsView(LoggedInMixin, ListView):
#	model = Request;
#	context_object_name = 'request_list';
#
#	template_name = 'home/service.html';
#	def get_queryset(self):
#		return Request.objects.all();

def cannotService(request):
	return render(request, 'home/notAdmin.html');

#def request_details(request, request_id):
#	if not request.user.is_staff:
#		return render(request, 'home/notAdmin.html')
#	current_request = get_object_or_404(Request, pk=request_id)
#	context = {
#		'current_request': current_request
#	}
#	return render(request, 'home/serviceReq.html', context)

#def service_request(request, request_id):
#	if not request.user.is_staff:
#		return render(request, 'home/notAdmin.html')
#	approve_deny = request.POST.get('select', None);
#	requestToService = get_object_or_404(Request, pk=request_id);
#	if (approve_deny == 'Approve'):
#		itemToChange = Item.objects.get(id=requestToService.item_id_id);
#		oldQuantity = itemToChange.count;
#		requestAmount = requestToService.quantity;
#		newQuantity = oldQuantity - requestAmount;
#		if newQuantity < 0:
#			return render(request, 'home/not_enough.html')
#		itemToChange.count = newQuantity;
#		requestToService.status = 'A';
#		itemToChange.save();
#	else:
#		requestToService.status = 'D';
#
#	admin_comment_fromReq = request.POST.get('comment', None);
#	requestToService.admin_comment = admin_comment_fromReq;
#	requestToService.save();
#	return render(request, 'home/request_success.html')

def request(request, item_id):
	item = get_object_or_404(Item, pk=item_id)
	try:
		current_cart = Cart_Request.objects.get(cart_owner=request.user, cart_status='P');
	except Cart_Request.DoesNotExist:
		current_cart = Cart_Request.objects.create(cart_owner=request.user, cart_status='P', cart_reason="(In Progress)")
		current_cart.save();
	if int(request.POST['quantity'])<1:
			return render(request, 'home/message.html', {'message':"Invalid quantity requested"})
	try:
		new_request = Request.objects.get(owner=request.user, item_id=item, status='P');
		new_request.quantity = request.POST['quantity'];
	except Request.DoesNotExist:
		new_request = Request(owner=request.user, item_id=item, quantity=request.POST['quantity'],\
			status='P', parent_cart=current_cart, reason='(In Progress)');
	new_request.save()
	return render(request, 'home/message.html', {'message':"Item Added to Cart"})

class DeleteRequestView(DeleteView):
	model = Request
	template_name = 'home/delete_request.html'

	def get_success_url(self):
		return reverse('index')

def delete_check(request, item_id):
	item = get_object_or_404(Item, pk=item_id)
	action = '/admin/delete_item/' + str(item_id) + "/";
	message = 'Deletion is permanent.  Are you sure you want to delete ' \
	+ item.item_name + "?";
	context = {
		'action':action,
		'message':message,
		'item':item,
		'submit_button':"Yes, delete " + str(item.item_name)
	}

	return render(request, 'manager/confirmation.html', context)

def delete_item(request, item_id):
	itemToDelete = get_object_or_404(Item, pk=item_id)
	itemToDelete.delete();
	return render(request, 'admin/delete_success.html');

def api_download(request):
	location = os.path.join(sys.path[0], "APIGuide.pdf")
	file = open(location, 'rb')
	content = file.read()
	file.close
	#serve the file
	response = HttpResponse(content, content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=api_guide.pdf'
	return response

def cart_request_details(request, cart_request_id):
	current_request = get_object_or_404(Cart_Request, pk=cart_request_id);
	subrequests = Request.objects.filter(parent_cart=current_request);
	context = {
		'current_request':current_request,
		'subrequests':subrequests,
	}
	return render(request, 'home/cart_request_details.html', context);
# class ListItemView(ListView):
#	 model=Item
#	 template_name='home/index.html'
#
# class ItemDetailView(DetailView):
#	 model=Item
#	 template_name='home/detail.html'

def checkout(request):
	try:
		to_checkout = Cart_Request.objects.get(cart_status='P', cart_owner=request.user);
	except Cart_Request.DoesNotExist:
		return render(request, 'home/message.html', {'message':"Cart Empty."});
	if request.method=='GET':
		checkout_form = CheckoutForm();
		subrequests = Request.objects.filter(parent_cart=to_checkout);
		context = {
			'subrequests':subrequests,
			'to_checkout':to_checkout,
			'checkout_form':checkout_form,
		}
		return render(request, 'home/checkout.html', context)
	else:
		# request.method == 'POST'
		checkout_form = CheckoutForm(request.POST);
		if checkout_form.is_valid():
			to_checkout.cart_reason = checkout_form.cleaned_data['cart_reason'];
			to_checkout.cart_status = 'O';
			to_checkout.suggestion = checkout_form.cleaned_data['loan_disburse'];
			to_checkout.save();
			message = 'You have requested:\n'
			subrequests = Request.objects.filter(parent_cart=to_checkout);
			for subrequest in subrequests:
				subrequest.status = 'O';
				subrequest.reason = to_checkout.cart_reason;
				subrequest.save();
				message+=subrequest.item_id.item_name+' x'+str(subrequest.quantity)+"\n"
			tag=EmailTag.objects.all()[0].tag
			subscribed_emails=SubscribedEmail.objects.all()
			bcc=[]
			for email in subscribed_emails:
				bcc.append(email.email)
			email = EmailMessage(
				tag+' Request',
				message,
				'from@example.com',
				[request.user.email],
				bcc
			)
			email.send()
		return HttpResponseRedirect('/checkout_success/')

def checkout_success(request):
	return render(request, 'home/message.html', {'message':"Request Placed!"})

def remove_request(request, request_id):
	to_remove = get_object_or_404(Request, pk=request_id);
	to_remove_parent = to_remove.parent_cart;
	to_remove.delete();
	if not Request.objects.filter(parent_cart=to_remove_parent).exists():
		to_remove_parent.delete();
		return render(request, 'home/message.html', {'message':"No Active Carts"})
	return HttpResponseRedirect('/checkout/')

def delete_request(request, cart_request_id):
	to_delete = get_object_or_404(Cart_Request, pk=cart_request_id);
	if request.method == 'GET':
		message = "Are you sure you want to delete this request? \n Reason: "\
		 + to_delete.cart_reason;
		action='/delete_request/' + str(cart_request_id) + '/';
		context = {
			'message':message,
			'submit_button': "Yes, Delete Request",
			'action':action,
		}
		return render(request, 'manager/confirmation.html', context)
	else:
		message = 'You have deleted your request for:\n'
		subrequests = Request.objects.filter(parent_cart=to_delete);
		for subrequest in subrequests:
			message+=subrequest.item_id.item_name+' x'+str(subrequest.quantity)+"\n"
			# subrequest.delete() ?
		to_delete.delete();
		tag=EmailTag.objects.all()[0].tag
		email = EmailMessage(
			tag+' Delete Request',
			message,
			'from@example.com',
			[request.user.email]
		)
		email.send()
		return HttpResponseRedirect('/delete_request_success/')

def loan_viewer(request):
	loan_list = Request.objects.filter(owner=request.user, status='L');
	return render(request, 'home/loan_viewer.html', {'loan_list':loan_list})

def delete_request_success(request):
	return render(request, 'home/message.html', {'message':'Request Removed.'})
