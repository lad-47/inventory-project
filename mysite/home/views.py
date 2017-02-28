from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Item, Request, Tag, CustomFieldEntry, CustomLongTextField, CustomShortTextField, CustomIntField, CustomFloatField, Cart_Request;
from .forms import CheckoutForm
from .serializers import ItemSerializer
# chance genereic.Listview stuff to ListView
from django.views.generic import View, DetailView, ListView, DeleteView, CreateView, FormView

from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import os, sys

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# item_list() above replaces this view!!!!!!!!!!!!
def index(request):
	latest_item_list = Item.objects.all()
	tag_list = Tag.objects.distinct('tag')
	if request.method == 'GET':  # If the form is submitted
		latest_item_list = Item.objects.all()
		search_query = request.GET.get('search_box', None)
		model_query = request.GET.get('model_box', None)
		tag_query = request.GET.getlist('select', None)
		extag_query = request.GET.getlist('exselect', None)
		if search_query is not None:
			latest_item_list = latest_item_list.filter(item_name__icontains=search_query)
		if model_query is not None:
			latest_item_list = latest_item_list.filter(model_number__icontains=model_query)
		if tag_query is not None and 'all' not in tag_query:
			for tag in tag_query:
				tag = Tag.objects.get(tag=tag);
				latest_item_list = latest_item_list.filter(tags=tag) 
		if extag_query is not None and 'none' not in extag_query:
			for tag in extag_query:
				   latest_item_list = latest_item_list.exclude(tag__tag=tag)
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
	if not request.user.is_authenticated():
		return render(request, 'home/detail.html', {'item':item})
	if request.user.is_staff:
		requests = Request.objects.filter(status='O');
	else:
		requests = Request.objects.filter(item_id=item.id, owner=request.user, status='O')

	custom_fields = CustomFieldEntry.objects.all()
	custom_values = []
	for cf in custom_fields:
		if request.user.is_staff or not cf.is_private:
			if cf.value_type == 'lt': # Long Text
				try:
					val = CustomLongTextField.objects.get(parent_item=item.id, field_name=cf)
					custom_values.append(val.field_name.field_name+": "+val.field_value)
				except CustomLongTextField.DoesNotExist:
					pass
			elif cf.value_type == 'st': # Short Text
				try:
					val = CustomShortTextField.objects.get(parent_item=item.id, field_name=cf)
					custom_values.append(val.field_name.field_name+": "+val.field_value)
				except CustomShortTextField.DoesNotExist:
					pass
			elif cf.value_type == 'int': # Integer
				try:
					val = CustomIntField.objects.get(parent_item=item.id, field_name=cf)
					custom_values.append(val.field_name.field_name+": "+str(val.field_value))
				except CustomIntField.DoesNotExist:
					pass
			elif cf.value_type == 'float': # Float
				try:
					val = CustomFloatField.objects.get(parent_item=item.id, field_name=cf)
					custom_values.append(val.field_name.field_name+": "+str(val.field_value))
				except CustomFloatField.DoesNotExist:
					pass
			else:
				return HttpResponseNotFound('<h1>Custom Field not found<h1>')
	context = {
		'item': item,
		'tags': tags,
		'requests': requests,
		'custom': custom_values
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
        'request':current_request,
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
        return render(request, 'home/message.html', {'message':"No Active Carts."});
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
            to_checkout.save();
            subrequests = Request.objects.filter(parent_cart=to_checkout);
            for subrequest in subrequests:
                subrequest.status = 'O';
                subrequest.reason = to_checkout.cart_reason;
                subrequest.save();
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
        to_delete.delete();
        return HttpResponseRedirect('/delete_request_success/')

def delete_request_success(request):
    return render(request, 'home/message.html', {'message':'Request Removed.'})
