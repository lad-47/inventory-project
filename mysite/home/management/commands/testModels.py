from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from home.models import User, Item, Request, Cart_Request, CustomFieldEntry, Tag, Asset

class Command(BaseCommand):
    def handle(self, **options):
        print(Cart_Request.objects.all()[0].pk);
        cart = Cart_Request.objects.get(pk=2);\
        jdk = User.objects.get(username="jdk2");
        a = Asset.objects.create(item_name="test_asset3", count=1, asset_tag="4")
        r = Request.objects.create(item_id=a, owner=jdk, quantity=1, reason="s", status='O', parent_cart=cart)
        print("test asset: ");
        print(r.item_id.item_name);
        print(r.item_id.asset.asset_tag);
       