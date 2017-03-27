from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from home.models import User, Item, Request, Cart_Request, CustomFieldEntry, Tag

class Command(BaseCommand):
    def handle(self, **options):
        jdk1 = User.objects.create_user(username='admin', \
        	password='yellowisacolor1', email=None);
        canService = Permission.objects.create(codename='can_service', \
        	name='Can Service Requests', \
        	content_type=ContentType.objects.get_for_model(Request));
        jdk1.user_permissions.add(canService);
        jdk1.is_superuser=True;
        jdk1.is_staff=True;
        jdk1.save();
        jdk2 = User.objects.create_user(username='jdk2', \
        	password='yellowisacolor2', email=None);
        resistor100ohm = Item.objects.create(item_name="Resistor 100 Ohm", \
        	count=10, model_number="R100", \
        	description="Resistor");
        resistor200ohm = Item.objects.create(item_name="Resistor 200 Ohm", \
        	count=10, model_number="R200", \
        	description="Resistor");


        resistor = Tag.objects.create(tag="Resistor");
        used = Tag.objects.create(tag="Used");
        r200ohms = Tag.objects.create(tag="200 ohms");

        resistor100ohm.tags.add(resistor);
        resistor200ohm.tags.add(resistor);
        resistor100ohm.tags.add(used);
        resistor200ohm.tags.add(r200ohms);
        
        #making some cart requests
        cartReq1 = Cart_Request.objects.create(cart_owner=jdk1, \
            cart_reason="Project Mayhem", cart_status='O');
        cartReq2 = Cart_Request.objects.create(cart_owner=jdk2, \
            cart_reason="Project Runway", cart_status='A');
        cartReq3 = Cart_Request.objects.create(cart_owner=jdk1, \
            cart_reason="Project MAGA", cart_status='O');
        cartReq4 = Cart_Request.objects.create(cart_owner=jdk2, \
            cart_reason="stupid lab", cart_status='O');

        #giving said cart requests some subrequests
        #right now there's a bug that if you ask for an item twice
        #it will thinkn you can service it even if you ask for 5 and 6 and 
        #there's only 10.
        jdk1Res100a = Request.objects.create(owner=jdk1, item_id=resistor100ohm,\
        	reason="because I need it", status='O', quantity='5', parent_cart=cartReq1);
        jdk1Res100b = Request.objects.create(owner=jdk1, item_id=resistor200ohm,\
            reason="because I need it", status='O', quantity='6', parent_cart=cartReq1);
        jdk2Res100c = Request.objects.create(owner=jdk1, item_id=resistor100ohm,\
            reason="because I need it", status='O', quantity='5', parent_cart=cartReq2);
        jdk2Res100d = Request.objects.create(owner=jdk1, item_id=resistor200ohm,\
            reason="because I need it", status='O', quantity='80', parent_cart=cartReq2);
        jdk1Res100f = Request.objects.create(owner=jdk1, item_id=resistor100ohm,\
            reason="because I need it", status='O', quantity='7', parent_cart=cartReq3);
        jdk1Res100g = Request.objects.create(owner=jdk1, item_id=resistor200ohm,\
            reason="because I need it", status='O', quantity='9', parent_cart=cartReq3);
        jdk2Res100h = Request.objects.create(owner=jdk1, item_id=resistor100ohm,\
            reason="because I need it", status='O', quantity='5', parent_cart=cartReq4);
        jdk2Res100i = Request.objects.create(owner=jdk1, item_id=resistor200ohm,\
            reason="because I need it", status='O', quantity='80', parent_cart=cartReq4);

        locationField = CustomFieldEntry.objects.create(field_name='Location', \
            is_private=False, value_type='st');
        testField = CustomFieldEntry.objects.create(field_name="TEST", \
            is_private=False, value_type='st');
       