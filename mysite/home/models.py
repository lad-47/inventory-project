from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class Tag(models.Model):
	#item_id = models.ForeignKey(Item, related_name='tags', on_delete=models.CASCADE)
	tag = models.CharField(max_length=100, unique=True);
	
	def __str__(self):
  		return self.tag

# if we add a field to this, we'll have to go add it to the
# ItemForm_factory properties dictionary as well, using the same name
class Item(models.Model):
	item_name = models.CharField(max_length=100, unique=True)
	count = models.PositiveIntegerField(default=0)
	model_number = models.CharField(max_length=100, null=True)
	description = models.TextField(null=True)
	tags = models.ManyToManyField(Tag);
	#location = models.CharField(max_length=100,null=True)
	def __str__(self):
		return self.item_name
	
	def get_absolute_url(self):
		return reverse('detail', kwargs={'item_id': self.id})


class Cart_Request(models.Model):
	STATUSES = (
	('O','Outstanding'),
	('A','Approved'),
	('D','Denied'),
	('P','In Progress'))
	cart_owner = models.ForeignKey(User, on_delete=models.CASCADE);
	cart_reason = models.TextField();
	cart_admin_comment = models.TextField(default="No Comment");
	cart_status = models.CharField(max_length=1, choices=STATUSES, default='O');
	
	def __str__(self):
		return self.tag

	
class Request(models.Model):
	STATUSES = (
	('O','Outstanding'),
	('A','Approved'),
	('D','Denied'),
	('P','In Progress'))
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

# This is a valid Custom Field that has been created
class CustomFieldEntry(models.Model):
	field_name = models.CharField(max_length=100, unique=True);
	is_private = models.BooleanField();
	value_type = models.CharField(max_length=10); # string key to indicate which type of value (lt,st,int,float)

#custom fields implemented using extra tables in the database
#in theory, "CustomField" should be an abstract class, but 
#I'm not totally sure how to implement that funcionality in python
class CustomField(models.Model):
	parent_item = models.ForeignKey(Item, on_delete=models.CASCADE);
	field_name = models.ForeignKey(CustomFieldEntry, on_delete=models.CASCADE);

class CustomLongTextField(CustomField):
	field_value = models.TextField();

class CustomShortTextField(CustomField):
	field_value = models.CharField(max_length=100);

class CustomIntField(CustomField):
	field_value = models.IntegerField();
	
class CustomFloatField(CustomField):
	field_value = models.FloatField();
	
class Log(models.Model):
	initiating_user = models.IntegerField(db_index=True)
	involved_item = models.IntegerField(null=True, blank=True, db_index=True)
	nature = models.TextField()
	timestamp = models.DateTimeField()
	related_request = models.IntegerField(null=True, blank=True, db_index=True)
	affected_user = models.IntegerField(null=True, blank=True, db_index=True)


