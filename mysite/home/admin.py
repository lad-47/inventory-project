from django.contrib import admin

from .models import Item

class ItemAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['item_name']}),
        ('Count information', {'fields': ['total_count']}),
    ]

admin.site.register(Item, ItemAdmin)