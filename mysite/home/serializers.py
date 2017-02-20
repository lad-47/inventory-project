from .models import Item,Request,Tag
from rest_framework import serializers
from django.contrib.auth.models import User

class MyPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    def to_representation(self, value):
        return str(value)

class ItemSerializer(serializers.ModelSerializer):
    tags = MyPrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False
     )
    
    class Meta:
        model = Item
        fields = ('item_name', 'count', 'model_number', 'description', 'location', 'tags')

        
class RequestSerializer(serializers.ModelSerializer):
    item_id = serializers.SlugRelatedField(
        queryset=Item.objects.all(),
        slug_field='item_name'
     )
    owner = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username'
     )
    admin_comment=serializers.CharField(required=False,allow_blank=True)
    class Meta:
        model = Request
        fields = ('owner','item_id','reason','admin_comment','quantity','status')
        
class UserSerializer(serializers.ModelSerializer):
    #requests = serializers.PrimaryKeyRelatedField(many=True,queryset=Request.objects.all())
    
    class Meta:
        model = User
        fields = ('id', 'username')
        
class UserCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('username','password')
        
        