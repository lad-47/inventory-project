from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class Item(models.Model):
	item_name = models.CharField(max_length=100)
	count = models.IntegerField(default=0)
	model_number = models.CharField(max_length=100, null=True)
	description = models.TextField(null=True)
	location = models.CharField(max_length=100,null=True)
	def __str__(self):
		return self.item_name
	
	def get_absolute_url(self):
		return reverse('detail', kwargs={'item_id': self.id})
		
class Tag(models.Model):
	item_id = models.ForeignKey(Item, related_name='tags', on_delete=models.CASCADE)
	tag = models.CharField(max_length=100)

class Cart_Request(models.Model):
	STATUSES = (
	('O','Outstanding'),
	('A','Approved'),
	('D','Denied'))
	cart_owner = models.ForeignKey(User, on_delete=models.CASCADE);
	cart_reason = models.TextField();
	cart_admin_comment = models.TextField(default="No Comment");
	cart_status = models.CharField(max_length=1, choices=STATUSES, default='O');
	is_active_request = models.BooleanField(default=True);
	
	def __str__(self):
		return self.tag

	
class Request(models.Model):
	STATUSES = (
	('O','Outstanding'),
	('A','Approved'),
	('D','Denied'))
	owner = models.ForeignKey(User, related_name='requests', on_delete=models.CASCADE, default=1)
	item_id = models.ForeignKey(Item, on_delete=models.CASCADE, default=1)
	reason = models.TextField()
	admin_comment = models.TextField(default="Unserviced");
	quantity = models.IntegerField(default=1);
	status = models.CharField(max_length=1, choices=STATUSES, default='O')
	#testField = models.IntegerField(default=0);
	parent_cart = models.ForeignKey(Cart_Request, null=True);

	def __str__(self):
		return "User: " + self.owner.__str__() + ", Item: " + \
		self.item_id.__str__() + " Reason: " + self.reason;

#custom fields implemented using extra tables in the database
#in theory, "CustomField" should be an abstract class, but 
#I'm not totally sure how to implement that funcionality in python
class CustomField(models.Model):
	parent_item = models.ForeignKey(Item, on_delete=models.CASCADE);
	field_name = models.CharField(max_length=100);
	is_private = models.BooleanField();

class CustomLongTextField(CustomField):
	field_value = models.TextField();

class CustomShortTextField(CustomField):
	field_value = models.CharField(max_length=70);

class CustomIntField(CustomField):
	field_value = models.IntegerField();
