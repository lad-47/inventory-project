from django import forms
from home.models import CustomFieldEntry, Item, Tag, BackfillPDF;

class CheckoutForm(forms.Form):
	cart_reason = forms.CharField(max_length=100, label="Request Reason:");
	l_d = (('D', 'Disbursement'), ('L', 'Loan'),  ('B', 'Backfill'))
	loan_disburse = forms.ChoiceField(widget=forms.RadioSelect, choices=l_d, label="Request Type");
	backfill_pdf = forms.FileField(required=False)