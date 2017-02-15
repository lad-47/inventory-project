from .models import Item,Request,Tag
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import six

class MyPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    def to_representation(self, value):
        return str(value)

class ItemSerializer(serializers.ModelSerializer):
    tags = MyPrimaryKeyRelatedField(allow_null=True, many=True, queryset=Tag.objects.all())
    
    class Meta:
        model = Item
        fields = ('item_name', 'count', 'model_number', 'description', 'location', 'tags')
        
class RequestSerializer(serializers.ModelSerializer):
    item_id = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())
    
    class Meta:
        model = Request
        fields = ('owner','item_id','reason','admin_comment','quantity','status')
        
class UserSerializer(serializers.ModelSerializer):
    requests = serializers.PrimaryKeyRelatedField(many=True, queryset=Request.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'requests')