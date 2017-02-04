from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
	item_name = models.CharField(max_length=100)
	total_count = models.IntegerField(default=0)
	total_available = models.IntegerField(default=0)
	model_number = models.CharField(max_length=100, null=True)
	description = models.TextField(null=True)
	location = models.CharField(max_length=100,null=True)
	def __str__(self):
		return self.item_name
		
class Tag(models.Model):
	item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
	tag = models.CharField(max_length=100)
	
class Request(models.Model):
	#STATUSES = (
	#('O','Outstanding'),
	#('A','Approved'),
	#('D','Denied'))
	#user_id = models.ForeignKey(User, on_delete=models.CASCADE)
	#item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
	reason = models.TextField()
	#status = models.CharField(max_length=1, choices=STATUSES)
	#testField = models.IntegerField(default=0);
	def __str__(self):
		return "Reason: " + self.reason;