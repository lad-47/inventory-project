from django import forms
from home.models import CustomFieldEntry, Item, Tag;

class ServiceForm(forms.Form):
	CHOICES = (('Approve', 'Approve'), ('Deny', 'Deny'));
	admin_comment = forms.CharField(max_length=200, required=False);
	approve_deny = forms.ChoiceField(widget=forms.RadioSelect, \
		choices=CHOICES);

def ItemForm_factory():

	# this is a hacky way to assemble the tag choices but python tuples are weird
	first = True;
	for item_tag in Tag.objects.all():
		if first:
			TAGS = ((item_tag.pk, item_tag.tag),);
			first = False;
			continue;
		TAGS = TAGS + ((item_tag.pk, item_tag.tag),);

	print('tags: ');
	print(TAGS);
	#TAGS = (('1', 'pick 1'), ('2', 'pick 2'));
	# class variables of the ItemForm class for which this is a factory
	properties = {
		'item_name': forms.CharField(max_length=100),
		'model_number': forms.CharField(),
		'description': forms.CharField(widget=forms.Textarea),
		'count': forms.IntegerField(min_value=0),
		'tags': forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, \
			choices=TAGS, required=False),
	}

	# add more class variables to properties for the custom fields
	custom_fields = CustomFieldEntry.objects.all();
	for cf in custom_fields:
		field_name = cf.field_name;
		field_type = cf.value_type;
		print(field_name);
		if field_type == 'st':
			properties[field_name] = forms.CharField(max_length=100, required=False)
		elif field_type == 'lt':
			properties[field_name] = forms.CharField(widget=forms.Textarea, required=False);
		elif field_type == 'int':
			properties[field_name] = forms.InegerField(required=False);
		elif field_type == 'float':
			properties[field_name] = forms.FloatField(required=False);

	# use python's magic 'type' method to create a class
	return type('ItemForm', (forms.Form,), properties);
