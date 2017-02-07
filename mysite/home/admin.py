from django.contrib import admin

from .models import Item, Tag, Request

class ItemAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['item_name']}),
        ('Count information', {'fields': ['total_count']}),
    ]
    
class RequestAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['user_id','item_id']}),
        ('Reason', {'fields': ['reason']}),
        ('Status', {'fields': ['status']})
    ]

admin.site.register(Item, ItemAdmin)
admin.site.register(Request, RequestAdmin)