from django.contrib import admin

from .models import Item, Tag, Request
from django.test.utils import tag

class TagInline(admin.TabularInline):
    model=Tag
    extra=1

class ItemAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['item_name']}),
        ('Starting Quantity', {'fields': ['total_count']}),
        ('Model Number', {'fields': ['model_number']}),
        ('Description', {'fields': ['description']}),
        ('Location', {'fields': ['location']}),
        #('Tags', {'fields': })
    ]
    inlines=[TagInline]
    
class RequestAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['user_id','item_id']}),
        ('Reason', {'fields': ['reason']}),
        ('Status', {'fields': ['status']})
    ]

admin.site.register(Item, ItemAdmin)
admin.site.register(Request, RequestAdmin)