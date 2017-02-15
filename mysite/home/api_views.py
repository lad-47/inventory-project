from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Item, Request, Tag;
from .serializers import ItemSerializer
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import copy

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'items': reverse('item-list', request=request, format=format),
    })

@api_view(['GET', 'POST'])
def item_list(request, format=None):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ItemSerializer(data=request.data)
        tags=[]
        if 'tags' in serializer.initial_data.keys():
            if isinstance(serializer.initial_data['tags'], str):
                tags.append(serializer.initial_data['tags'])
            else:
                for tag in serializer.initial_data['tags']:
                    tags.append(tag)
            del serializer.initial_data['tags']
        if serializer.is_valid():
            serializer.save()
            for tag in tags:
                new_tag=Tag(item_id=Item.objects.get(item_name=serializer.data['item_name']),tag=tag)
                new_tag.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def item_detail(request, pk, format=None):
    """
    Retrieve, update or delete a snippet instance.
    """
    try:
        item = Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    