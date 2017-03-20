from .models import Item,Request,Tag,CustomShortTextField,CustomLongTextField,CustomIntField,CustomFloatField,CustomFieldEntry,Log
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
        fields = ('item_name', 'count', 'model_number', 'description', 'tags')

class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = ('tag',)
        
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
        fields = ('owner','item_id','reason', 'admin_comment','quantity','status')
        
class UserSerializer(serializers.ModelSerializer):
    #requests = serializers.PrimaryKeyRelatedField(many=True,queryset=Request.objects.all())
    
    class Meta:
        model = User
        fields = ('id', 'username')
        
class UserCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('username','password')
        
class CustomFieldEntrySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomFieldEntry
        fields = ('field_name','is_private','value_type')
        
class CustomShortTextFieldSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomShortTextField
        fields = ('parent_item','field_name','field_value')
        
class CustomLongTextFieldSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomLongTextField
        fields = ('parent_item','field_name','field_value')
        
class CustomIntFieldSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomIntField
        fields = ('parent_item','field_name','field_value')
        
class CustomFloatFieldSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomFloatField
        fields = ('parent_item','field_name','field_value')
        
class LogSerializer(serializers.ModelSerializer):
    #requests = serializers.PrimaryKeyRelatedField(many=True,queryset=Request.objects.all())
    
    class Meta:
        model = Log
        fields = ('initiating_user','initiating_username','involved_item','involved_item_name','nature','timestamp','related_request','affected_user','affected_username')

        
        