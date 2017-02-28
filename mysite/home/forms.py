from django import forms
from home.models import CustomFieldEntry, Item, Tag;

class CheckoutForm(forms.Form):
	cart_reason = forms.CharField(max_length=100, label="Request Reason:");