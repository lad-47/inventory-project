from django.shortcuts import render
from home.models import Request, Cart_Request, User, Item

def manager_home(request):
	return render(request, 'manager/manager_home.html');

def cart_request_details(request, request_id):
	#check if the user is a manager
    if not request.user.is_staff:
        return render(request, 'home/notAdmin.html')
    current_cart_request = get_object_or_404(Request, pk=cart_request_id)
    subrequests = Request.objects.filter(parent_cart=cart_request_id)
    new_quantities = [];
    request_validities = [];
    for subrequest in subrequests:
        itemToChange = Item.objects.get(id=subrequest.item_id_id);
        oldQuantity = itemToChange.total_available;
        requestAmount = subrequest.quantity;
        newQuantity = oldQuantity - requestAmount;
        new_quantities+=[newQuantity];
        request_validities+=[not (newQuantity < 0)];
    #pass the cart_request and all of its children
    #also, pass arrays with the new quantities of items after servicing request,
    #plus whether those requests can be serviced
    context = {
        'current_cart_request': current_cart_request, 
        'subrequests': subrequests,
        'new_quantities': new_quantities,
        'request_validities': request_validities
    }
    return render(request, 'manager/cart_requests.html', context)

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