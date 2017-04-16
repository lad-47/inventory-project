from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class Tag(models.Model):
	#item_id = models.ForeignKey(Item, related_name='tags', on_delete=models.CASCADE)
	tag = models.CharField(max_length=100, unique=True);
	
	def __str__(self):
  		return self.tag

class AbstractItem(models.Model):
	item_name = models.CharField(max_length=100)
	count = models.PositiveIntegerField(default=0)
	model_number = models.CharField(max_length=100, null=True)
	description = models.TextField(null=True)
	tags = models.ManyToManyField(Tag);
	is_asset = models.BooleanField(default=False);

	#location = models.CharField(max_length=100,null=True)
	def __str__(self):
		return self.item_name
	
	def get_absolute_url(self):
		return reverse('detail', kwargs={'item_id': self.id})


# if we add a field to this, we'll have to go add it to the
# ItemForm_factory properties dictionary as well, using the same name
class Item(AbstractItem):
	#put item name in this field to throw non-unique exception
	name_unique_check = models.CharField(max_length=100, unique=True, null=True)

class Asset(AbstractItem):
	asset_tag = models.PositiveIntegerField(unique=True);



class Cart_Request(models.Model):
	STATUSES = (
	('O','Outstanding'),
	('A','Approved'),
	('D','Denied'),
	('P','In Progress'),
	('L','Loaned'),
	('B','Backfill'))
	SUGG = (('D', 'Disbursement'), ('L', 'Loan'))
	cart_owner = models.ForeignKey(User, on_delete=models.CASCADE);
	cart_reason = models.TextField();
	cart_admin_comment = models.TextField(default="No Comment");
	cart_status = models.CharField(max_length=1, choices=STATUSES, default='O');
	suggestion = models.CharField(max_length=1, choices=SUGG, default='D')

	
class Request(models.Model):
	STATUSES = (
	('O','Outstanding'),
	('A','Disbursed'),
	('D','Denied'),
	('P','In Progress'),
	('L','Loaned'),
	('R','Returned'),
	('B','For Backfill'),
	('Z','Hacky Log Status'))
	owner = models.ForeignKey(User, related_name='requests', on_delete=models.CASCADE, default=1)
	item_id = models.ForeignKey(AbstractItem, on_delete=models.CASCADE, default=1)
	reason = models.TextField()
	admin_comment = models.TextField(default="No Comment");
	quantity = models.PositiveIntegerField(default=1);
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
	per_asset = models.BooleanField(default=False);
#custom fields implemented using extra tables in the database
#in theory, "CustomField" should be an abstract class, but 
#I'm not totally sure how to implement that funcionality in python
class CustomField(models.Model):
	parent_item = models.ForeignKey(AbstractItem, on_delete=models.CASCADE);
	field_name = models.ForeignKey(CustomFieldEntry, on_delete=models.CASCADE);

class CustomLongTextField(CustomField):
	field_value = models.TextField(null=True);

class CustomShortTextField(CustomField):
	field_value = models.CharField(null=True, max_length=100);

class CustomIntField(CustomField):
	field_value = models.IntegerField(null=True);
	
class CustomFloatField(CustomField):
	field_value = models.FloatField(null=True);
	
class Log(models.Model):
	initiating_user = models.IntegerField(db_index=True)
	initiating_username = models.CharField(max_length=150)
	involved_item = models.IntegerField(null=True, blank=True, db_index=True)
	involved_item_name = models.CharField(max_length=100, null=True, blank=True)
	nature = models.TextField()
	timestamp = models.DateTimeField()
	related_request = models.IntegerField(null=True, blank=True, db_index=True)
	affected_user = models.IntegerField(null=True, blank=True, db_index=True)
	affected_username = models.CharField(max_length=150, null=True, blank=True)

class SubscribedEmail(models.Model):
	email=models.EmailField()
	
class EmailBody(models.Model):
	body=models.TextField()
	
class EmailTag(models.Model):
	tag=models.CharField(max_length=50)
	
class LoanDate(models.Model):
	date=models.DateField()
