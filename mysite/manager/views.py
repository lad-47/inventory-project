from django.shortcuts import get_object_or_404, render
from home.models import Request, Cart_Request, User, Item

def manager_home(request):
	return render(request, 'manager/manager_home.html');

def cart_requests(request):
	#check if the user is a manager
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	cart_requests = Cart_Request.objects.all();
	cart_requests_and_v = [];
	#determine if each request can be serviced or not
	for cart_request in cart_requests:
		subrequests = Request.objects.filter(parent_cart=cart_request);
		valid = True;
		for subrequest in subrequests:
			itemToChange = Item.objects.get(id=subrequest.item_id_id);
			oldQuantity = itemToChange.total_available;
			requestAmount = subrequest.quantity;
			newQuantity = oldQuantity - requestAmount;
			if newQuantity < 0:
				valid = False;
				break;
		cart_requests_and_v += [(cart_request, valid)];
    #pass the cart_request and all of its children
    #also, pass arrays with the new quantities of items after servicing request,
    #plus whether those requests can be serviced
	context = {
        'cart_requests_and_v': cart_requests_and_v
	}
	return render(request, 'manager/cart_requests.html', context)

def cart_request_details(request, cart_request_id):
	if not request.user.is_staff:
		return render(request, 'home/notAdmin.html')
	current_request = get_object_or_404(Cart_Request, pk=cart_request_id);
	subrequests = Request.objects.filter(parent_cart_id=cart_request_id);
	req_info = [];
	for subrequest in subrequests:
		itemToChange = Item.objects.get(id=subrequest.item_id_id);
		oldQuantity = itemToChange.total_available;
		requestAmount = subrequest.quantity;
		newQuantity = oldQuantity - requestAmount;
		valid = not (newQuantity < 0)
		req_info+=[(subrequest, requestAmount, oldQuantity, valid)];
	context = {
		'current_request': current_request,
		'req_info': req_info,
	}
	return render(request, 'manager/cart_request_details.html', context);

def service_cart_request(request, cart_request_id):
	#check if user is a manager
    if not request.user.is_staff:
        return render(request, 'home/notAdmin.html')

    approve_deny = request.POST.get('select', None);

    #get the cart_request from the id passed
    current_cart_request = get_object_or_404(Cart_Request, pk=cart_request_id);
    subrequests = Request.objects.filter(parent_cart=current_cart_request);

    #if the request was approved, check validity first
    if (approve_deny == 'Approve'):    
        itemToChange = Item.objects.get(id=requestToService.item_id_id);
        oldQuantity = itemToChange.total_available;
        requestAmount = requestToService.quantity;
        newQuantity = oldQuantity - requestAmount;
        if newQuantity < 0:
            return render(request, 'home/not_enough.html')
        itemToChange.total_available = newQuantity;
        requestToService.status = 'A';
        itemToChange.save();
    else:
        requestToService.status = 'D';
	
    admin_comment_fromReq = request.POST.get('comment', None);
    requestToService.admin_comment = admin_comment_fromReq;
    requestToService.save();
    return render(request, 'home/request_success.html')