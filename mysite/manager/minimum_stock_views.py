from home.models import Item,Tag
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
import ast

def minimum_stock_bulk_set(request):
    if not request.user.is_staff:
        return render(request, 'home/notAdmin.html')
    latest_item_list = Item.objects.all()
    tag_list = Tag.objects.distinct('tag')
        
    search_param=request.GET.get('search_box','#not_valid#')
    model_param=request.GET.get('model_box','#not_valid#')
    tag_param=request.GET.getlist('myTags[]',['#not_valid#'])
    extag_param=request.GET.getlist('exTags[]',['#not_valid#'])
    
    if request.method == 'POST':
        item_list = get_items(request.POST.get('search_param'), request.POST.get('model_param'), ast.literal_eval(request.POST.get('tag_param')), ast.literal_eval(request.POST.get('extag_param')))
        for item in item_list:
            print("1: ")
            print(item)
            item.minimum_stock = int(request.POST.get('quantity'))
            item.save()
    if request.method == 'GET':  # If the form is submitted
        search_query = request.GET.get('search_box', None)
        model_query = request.GET.get('model_box', None)
        tag_query = request.GET.getlist('myTags[]', None)
        extag_query = request.GET.getlist('exTags[]', None)
        
        latest_item_list = get_items(search_query,model_query,tag_query,extag_query)
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
        'tag_list': tag_list,
        'search_param': search_param,
        'model_param': model_param,
        'tag_param': tag_param,
        'extag_param': extag_param
    }
    return render(request, 'manager/minimum_stock_bulk_set.html', context)

def get_items(search, model, tags, extags):
    print("XXX")
    latest_item_list = Item.objects.all()
    if search is not None and search != '#not_valid#':
        print("search: "+search)
        latest_item_list = latest_item_list.filter(item_name__icontains=search)
    if model is not None and model != '#not_valid#':
        print("model: "+model)
        latest_item_list = latest_item_list.filter(model_number__icontains=model)
    if tags is not None:
        print("tags: ")
        print(tags)
        for tag in tags:
            print("tag: "+tag)
            if (tag != '') and (tag != '#not_valid#'):
                try:
                    tag = Tag.objects.get(tag=tag);
                    latest_item_list = latest_item_list.filter(tags=tag)
                except Tag.DoesNotExist:
                    latest_item_list = Item.objects.none()
    if extags is not None:
        for tag in extags:
            if (tag != '') and (tag != '#not_valid#'):
                try:
                    tag = Tag.objects.get(tag=tag)
                    latest_item_list = latest_item_list.exclude(tags=tag)
                except Tag.DoesNotExist:
                    pass
    latest_item_list = sorted(latest_item_list, key=lambda item: item.item_name)
    return latest_item_list

    