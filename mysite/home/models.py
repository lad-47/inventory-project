from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class Item(models.Model):
	item_name = models.CharField(max_length=100)
	total_count = models.IntegerField(default=0)
	total_available = models.IntegerField(default=0)
	model_number = models.CharField(max_length=100, null=True)
	description = models.TextField(null=True)
	location = models.CharField(max_length=100,null=True)
	def __str__(self):
		return self.item_name
	
	def get_absolute_url(self):
		return reverse('detail', kwargs={'item_id': self.id})
		
class Tag(models.Model):
	item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
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
	
class Request(models.Model):
	STATUSES = (
	('O','Outstanding'),
	('A','Approved'),
	('D','Denied'))
	owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
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

