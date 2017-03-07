from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Item, Request, Tag, CustomShortTextField, CustomLongTextField, CustomIntField, CustomFloatField, CustomFieldEntry
from .serializers import ItemSerializer, RequestSerializer, UserSerializer, UserCreateSerializer, CustomShortTextFieldSerializer, CustomLongTextFieldSerializer, CustomIntFieldSerializer,CustomFloatFieldSerializer,CustomFieldEntrySerializer
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
        'users': reverse('user-list', request=request, format=format),
        'custom fields': reverse('api-custom', request=request, format=format)
    })
    
@api_view(['GET'])
def custom_root(request, format=None):
    return Response({
        'entries': reverse('custom-list', request=request, format=format),
        'shorts': reverse('short-list', request=request, format=format),
        'longs': reverse('long-list', request=request, format=format),
        'ints': reverse('int-list', request=request, format=format),
        'floats': reverse('float-list', request=request, format=format)
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
                item = Item.objects.get(item_name=serializer.data['item_name'])
                for tag in tags:
                    try: 
                        Tag.objects.get(tag=tag)
                        tag_object=Tag.objects.get(tag=tag)
                        tag_object.item_set.add(item)
                        tag_object.save()
                        item.save()
                    except Tag.DoesNotExist:
                        tag_object=Tag(tag=tag)
                        tag_object.save()
                        tag_object.item_set.add(item)
                        tag_object.save()
                        item.save()
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
                item = Item.objects.get(item_name=serializer.data['item_name'])
                for tag in item.tags.all():
                    if tag.tag not in tags:
                        tag.delete()
                        item.save()
                for tag in tags:
                    try: 
                        item.tags.get(tag=tag)
                    except Tag.DoesNotExist:
                        try:
                            Tag.objects.get(tag=tag)
                            tag_object=Tag.objects.get(tag=tag)
                            tag_object.item_set.add(item)
                            tag_object.save()
                            item.save()
                        except Tag.DoesNotExist:
                            tag_object=Tag(tag=tag)
                            tag_object.save()
                            tag_object.item_set.add(item)
                            tag_object.save()
                            item.save()
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

@api_view(['GET', 'POST'])
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
        except User.DoesNotExist:
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
    
def get_token(request):
    if request.user.is_authenticated():
        token, created = Token.objects.get_or_create(user=request.user)
        context = {
            'token': token.key
        }
        return render(request, 'home/get_token.html', context);
    return render(request, 'home/notAdmin.html')

@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def custom_list(request, format=None):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        if request.user.is_staff:
            fields = CustomFieldEntry.objects.all()
            serializer = CustomFieldEntrySerializer(fields, many=True)
            return Response(serializer.data)
        else:
            fields = CustomFieldEntry.objects.filter(is_private=False)
            serializer = CustomFieldEntrySerializer(fields, many=True)
            return Response(serializer.data)
    
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def custom_detail(request, pk, format=None):
    """
    Retrieve, update or delete a snippet instance.
    """
    if request.user.is_staff:
        try:
            field = CustomFieldEntry.objects.get(pk=pk)
        except CustomFieldEntry.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
        if request.method == 'GET':
            serializer = CustomFieldEntrySerializer(field)
            return Response(serializer.data)
    
        elif request.method == 'PUT':
            serializer = CustomFieldEntrySerializer(field, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        elif request.method == 'DELETE':
            field.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    return Response('Manager Permission Required')


@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def short_list(request, format=None):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        if request.user.is_staff:
            shorts = CustomShortTextField.objects.all()
            serializer = CustomShortTextFieldSerializer(shorts, many=True)
            return Response(serializer.data)
        else:
            shorts = CustomShortTextField.objects.filter(field_name__is_private=False)
            serializer = CustomShortTextFieldSerializer(shorts, many=True)
            return Response(serializer.data)
    
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def short_detail(request, pk, format=None):
    """
    Retrieve, update or delete a snippet instance.
    """
    if request.user.is_staff:
        try:
            short = CustomShortTextField.objects.get(pk=pk)
        except CustomShortTextField.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
        if request.method == 'GET':
            serializer = CustomShortTextFieldSerializer(short)
            return Response(serializer.data)
    
        elif request.method == 'PUT':
            serializer = CustomShortTextFieldSerializer(short, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        elif request.method == 'DELETE':
            short.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    return Response('Manager Permission Required')

@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def long_list(request, format=None):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        if request.user.is_staff:
            longs = CustomLongTextField.objects.all()
            serializer = CustomLongTextFieldSerializer(longs, many=True)
            return Response(serializer.data)
        else:
            longs = CustomLongTextField.objects.filter(field_name__is_private=False)
            serializer = CustomLongTextFieldSerializer(longs, many=True)
            return Response(serializer.data)
    
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def long_detail(request, pk, format=None):
    """
    Retrieve, update or delete a snippet instance.
    """
    if request.user.is_staff:
        try:
            long = CustomLongTextField.objects.get(pk=pk)
        except CustomLongTextField.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
        if request.method == 'GET':
            serializer = CustomLongTextFieldSerializer(long)
            return Response(serializer.data)
    
        elif request.method == 'PUT':
            serializer = CustomLongTextFieldSerializer(long, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        elif request.method == 'DELETE':
            long.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    return Response('Manager Permission Required')

@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def int_list(request, format=None):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        if request.user.is_staff:
            nums = CustomIntField.objects.all()
            serializer = CustomIntFieldSerializer(nums, many=True)
            return Response(serializer.data)
        else:
            nums = CustomIntField.objects.filter(field_name__is_private=False)
            serializer = CustomIntFieldSerializer(nums, many=True)
            return Response(serializer.data)
    
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def int_detail(request, pk, format=None):
    """
    Retrieve, update or delete a snippet instance.
    """
    if request.user.is_staff:
        try:
            num = CustomIntField.objects.get(pk=pk)
        except CustomIntField.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
        if request.method == 'GET':
            serializer = CustomIntFieldSerializer(num)
            return Response(serializer.data)
    
        elif request.method == 'PUT':
            serializer = CustomIntFieldSerializer(num, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        elif request.method == 'DELETE':
            num.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    return Response('Manager Permission Required')

@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def float_list(request, format=None):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        if request.user.is_staff:
            nums = CustomFloatField.objects.all()
            serializer = CustomFloatFieldSerializer(nums, many=True)
            return Response(serializer.data)
        else:
            nums = CustomFloatField.objects.filter(field_name__is_private=False)
            serializer = CustomFloatFieldSerializer(nums, many=True)
            return Response(serializer.data)
    
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@permission_classes((IsAuthenticated,))
def float_detail(request, pk, format=None):
    """
    Retrieve, update or delete a snippet instance.
    """
    if request.user.is_staff:
        try:
            num = CustomFloatField.objects.get(pk=pk)
        except CustomFloatField.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
        if request.method == 'GET':
            serializer = CustomFloatFieldSerializer(num)
            return Response(serializer.data)
    
        elif request.method == 'PUT':
            serializer = CustomFloatFieldSerializer(num, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        elif request.method == 'DELETE':
            num.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    return Response('Manager Permission Required')


