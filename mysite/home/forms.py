from django import forms

class ServiceReqForm(forms.Form):
	comment = forms.CharField(max_length=200);