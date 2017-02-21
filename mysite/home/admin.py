from django.contrib import admin

from .models import Item, Tag, Request
from django.test.utils import tag

class TagInline(admin.TabularInline):
    model=Tag
    extra=1

class ItemAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Item', {'fields': ['item_name']}),
        ('Starting Quantity', {'fields': ['count']}),
        ('Model Number', {'fields': ['model_number']}),
        ('Description', {'fields': ['description']}),
        ('Location', {'fields': ['location']}),
        #('Tags', {'fields': })
    ]
    inlines=[TagInline]
    
class RequestAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['owner','item_id']}),
        ('Reason', {'fields': ['reason']}),
        ('Status', {'fields': ['status']}),
        ('Comment', {'fields': ['admin_comment']})
    ]

admin.site.register(Item, ItemAdmin)
admin.site.register(Request, RequestAdmin)