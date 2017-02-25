from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def users(request):
    if not request.user.is_superuser:
        return render(request, 'home/notAdmin.html')
    users = User.objects.all()
    if request.method == 'GET':  # If the form is submitted
        user_query = request.GET.get('user_box', None)
        if user_query is not None and not user_query=="":
            try:
                users = User.objects.filter(username=user_query)
            except User.DoesNotExist:
                context = {
                    'users': users,
                    'error': "User does not exist" }
                return render(request, 'administrator/users.html', context)
    page = request.GET.get('page', 1)
    paginator = Paginator(users, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        'users': users
    }
    return render(request, 'administrator/users.html', context)

def create_user(request):
    if not request.user.is_superuser:
        return render(request, 'home/notAdmin.html')
    # on a post we (print) the data and then return success
    if request.method == 'POST':
        username = request.POST.get('username_box', None)
        password = request.POST.get('password_box', None)
        user = User.objects.create_user(username=username,password=password)
        user.save()
        return HttpResponseRedirect('/manager/create_success');

    return render(request, 'administrator/create_user.html')

def detail_user(request, user_id):
    if not request.user.is_superuser:
        return render(request, 'home/notAdmin.html')
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        if request.POST.get('manager_box', None)=='manager':
            user.is_staff=True
            user.save()
        else:
            user.is_staff=False
            user.is_superuser=False
            user.save()
        if request.POST.get('admin_box', None)=='admin':
            user.is_superuser=True
            user.is_staff=True
            user.save()
        else:
            user.is_superuser=False
            user.save()
    context = {
        'edit_user': user
    }
    return render(request, 'administrator/detail_user.html', context)


