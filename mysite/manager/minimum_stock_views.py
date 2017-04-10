from home.models import Item,Tag,
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

def minimum_stock_bulk_set(request):
    if not request.user.is_staff:
        return render(request, 'home/notAdmin.html')
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
                #     this_tag = Tag.objects.get(tag=tag)
                #     tags_to_include.append(this_tag)
                if (tag != ''):
                    tag = Tag.objects.get(tag=tag);
                    latest_item_list = latest_item_list.filter(tags=tag)
            # if tags_to_include is not None:
            #     latest_item_list = latest_item_list.filter(tags__in=tags_to_include)
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
    return render(request, 'manager/minimum_stock_bulk_set.html', context)