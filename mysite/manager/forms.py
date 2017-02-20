from django import forms

class ServiceForm(forms.Form):
	CHOICES = (('Approve', 'Approve'), ('Deny', 'Deny'));
	admin_comment = forms.CharField(max_length=200, required=False);
	approve_deny = forms.ChoiceField(widget=forms.RadioSelect, \
		choices=CHOICES);
