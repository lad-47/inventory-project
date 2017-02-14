from .models import Item
from rest_framework import serializers

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('item_name', 'count', 'model_number', 'description', 'location')