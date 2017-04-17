from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#from .forms import CFAddForm, CFDeleteForm
from home.models import CustomFieldEntry
from .import_logic import import_data

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
        confirm_password = request.POST.get('confirm_password_box', None)
        email = request.POST.get('email_box', None)
        if password != confirm_password:
            error = "Passwords must match!"
            context = {
                'error': error,
                'username': username,
                'email': email
            }
            return render(request, 'administrator/create_user.html', context)
        user = User.objects.create_user(username=username,email=email,password=password)
        user.save()
        return render(request, 'manager/success.html', {'message':"User was created successfully."});

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
        return HttpResponseRedirect('/admin/users');
    context = {
        'edit_user': user
    }
    return render(request, 'administrator/detail_user.html', context)

def cf_manager(request):
    #delete_form = CFDeleteForm(); deprecated
    if request.method == 'POST':
        add_form = CFAddForm(request.POST);
        if add_form.is_valid():
            vt = add_form.cleaned_data['value_type'];
            fn = add_form.cleaned_data['field_name'];
            i_p = add_form.cleaned_data['is_private'];
            p_a = add_form.cleaned_data['per_asset'];
            new_field = CustomFieldEntry.objects.create(value_type=vt, \
                field_name=fn, is_private=i_p, per_asset=p_a);
            new_field.save();
            return HttpResponseRedirect('/admin/custom_fields/create/success/');
    else:
        add_form = CFAddForm();

    cfs = CustomFieldEntry.objects.all()

    context = {
        'add_form':add_form,
        #'delete_form':delete_form, deprecated
        'cfs':cfs
    }

    return render(request, 'administrator/cf_manager.html', context);

def cf_delete_conf(request):
    # confirm delete of custom fields
    if request.method == 'POST':
        delete_form = CFDeleteForm(request.POST);
        if delete_form.is_valid():
            message = "Are you sure you want to delete these fields?";
            submit = "Yes, Delete Fields";
            action = '/admin/custom_fields/delete_action/';
            context = {
                'form':delete_form,
                'message':message,
                'submit_button':submit,
                'action':action,
            }
            return render(request, 'manager/confirmation.html', context);
        else:
            context = {
                'delete_form':delete_form,
                'add_form': CFAddForm(),
            }
            return render(request, 'administrator/cf_manager.html', context);

    # we shoudldn't get here with a GET
    return render(request, 'index.html');

def cf_delete_action(request):
    if request.method == 'POST':
        delete_cfs = request.POST.getlist('deleteCFs[]', None)
        if delete_cfs is not None:
            for cf in delete_cfs:
                try:
                    cf_instance = CustomFieldEntry.objects.get(field_name=cf)
                    cf_instance.delete()
                except:
                    # User entered non-existent Custom Field
                    pass
            return HttpResponseRedirect('/admin/custom_fields/delete/success/')

        """ deprecated form code
        delete_form = CFDeleteForm(request.POST);
        if delete_form.is_valid():
            for cfPK in delete_form.cleaned_data['to_delete']:
                cf = CustomFieldEntry.objects.get(pk=cfPK);
                cf.delete();
                return HttpResponseRedirect('/admin/custom_fields/delete/success/');"""
        add_form = CFAddForm();
        context = {
            #'delete_form':delete_form,
            'add_form':add_form,
        }
        return render(request, 'administrator/cf_manager.html', context);
    # we shoudldn't get here with a GET
    return render(request, 'index.html');

def cf_delete_success(request):
    return render(request, 'manager/success.html', {'message':"Fields Successfully Deleted."});

def cf_create_success(request):
    return render(request, 'manager/success.html', {'message': "Field Successfully Created."})

def bulk_import(request):
    if not request.user.is_superuser:
        return render(request, 'home/notAdmin.html')
    if request.method == 'POST':
        raw_data = request.POST.get('import_data', None);
        if raw_data is not None:
            # process/import data and show success/failure to user
            status = import_data(raw_data)
            #print(str(status))
            if status == "OK":
                return render(request, 'manager/success.html', {'message':"Data was imported and saved correctly."})
            else:
                return render(request, 'administrator/import_failure.html', {'message':str(status)})
        else:
            return render(request, 'administrator/import_failure.html', {'message':"Data was not retrieved correctly."})
    return render(request, 'administrator/bulk_import.html')
