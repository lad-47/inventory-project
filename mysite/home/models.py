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
	
class Request(models.Model):
	STATUSES = (
	('O','Outstanding'),
	('A','Approved'),
	('D','Denied'))
	user_id = models.ForeignKey(User, on_delete=models.CASCADE)
	item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
	reason = models.TextField()
	status = models.CharField(max_length=1, choices=STATUSES)
	
	