from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from home.models import User, Item, Request

class Command(BaseCommand):
    def handle(self, **options):
        jdk1 = User.objects.create_user(username='jdk1', \
        	password='yellowisacolor1', email=None);
        canService = Permission.objects.create(codename='can_service', \
        	name='Can Service Requests', \
        	content_type=ContentType.objects.get_for_model(Request));
        jdk1.user_permissions.add(canService);

        jdk2 = User.objects.create_user(username='jdk2', \
        	password='yellowisacolor2', email=None);
        resistor100ohm = Item.objects.create(item_name="Resistor 100 Ohm", \
        	total_count=10, total_available=10, model_number="R100", \
        	description="Resistor", location="Hudson");
        resistor200ohm = Item.objects.create(item_name="Resistor 200 Ohm", \
        	total_count=10, total_available=10, model_number="R200", \
        	description="Resistor", location="Hudson");
        jdk1Res100 = Request.objects.create(owner=jdk1, item_id=resistor100ohm,\
        	reason="because I need it", status='O', quantity='5');
        jdk2Res200 = Request.objects.create(owner=jdk2, item_id=resistor200ohm, \
        	reason="hugh mungus what?", status='O');