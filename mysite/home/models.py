from django.db import models


class Item(models.Model):
	item_name = models.CharField(max_length=200)
	count = models.IntegerField(default=0)
	def __str__(self):
		return self.item_name