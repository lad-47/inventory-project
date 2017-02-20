from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Item, Request, Tag;
from .serializers import ItemSerializer, RequestSerializer, UserSerializer, UserCreateSerializer
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication,\
    SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'items': reverse('item-list', request=request, format=format),
        'requests': reverse('request-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format)
    })

@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def item_list(request, format=None):
    """
    List all items, or create a new item.
    curl -X GET -H "Authorization: Token <insert API token>" https://<insert project domain>/api/item
    """
    if request.method == 'GET':
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        response = Response(serializer.data)
        return response

    elif request.method == 'POST':
        if request.user.is_staff:
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
        return Response('Manager Permission Required')

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
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
        if request.user.is_staff:
            serializer = ItemSerializer(item, data=request.data)
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
                for tag in Tag.objects.filter(item_id=Item.objects.get(item_name=serializer.data['item_name'])):
                    if tag.tag not in tags:
                        tag.delete()
                for tag in tags:
                    try: 
                        Tag.objects.get(item_id=Item.objects.get(item_name=serializer.data['item_name']),tag=tag)
                    except Tag.DoesNotExist:
                        new_tag=Tag(item_id=Item.objects.get(item_name=serializer.data['item_name']),tag=tag)
                        new_tag.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('Manager Permission Required')

    elif request.method == 'DELETE':
        if request.user.is_superuser:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Administrator Permission Required')
    
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def request_list(request, format=None):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        if request.user.is_staff:
            requests = Request.objects.all()
        else:
            requests = Request.objects.filter(owner=request.user)
        serializer = RequestSerializer(requests, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = RequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def request_detail(request, pk, format=None):
    """
    Retrieve, update or delete a snippet instance.
    """
    try:
        request_object = Request.objects.get(pk=pk)
    except Request.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if request_object.owner == request.user or request.user.is_staff:
            serializer = RequestSerializer(request_object)
            return Response(serializer.data)
        return Response('Manager Permission Required')

    elif request.method == 'PUT':
        if request_object.owner == request.user or request.user.is_staff:
            serializer = RequestSerializer(request_object, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('Manager Permission Required')

    elif request.method == 'DELETE':
        if request_object.owner == request.user:
            request_object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Owner Permission Required')

@api_view(['GET'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def user_list(request, format=None):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        if request.user.is_staff:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        return Response('Manager Permission Required')
    
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def user_detail(request, pk, format=None):
    """
    Retrieve, update or delete a snippet instance.
    """
    if request.user.is_staff:
        try:
            user = User.objects.get(pk=pk)
        except Request.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
    
        elif request.method == 'PUT':
            serializer = UserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        elif request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    return Response('Manager Permission Required')
    
@api_view(['POST'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def user_create(request, format=None):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'POST':
        if request.user.is_superuser:
            serializer = UserCreateSerializer(data=request.data)
            if serializer.is_valid():
                user = User.objects.create_user(username=serializer.data['username'],password=serializer.data['password'])
                user.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('Administrator Permission Required')
