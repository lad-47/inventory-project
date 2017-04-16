from django import forms
from home.models import CustomFieldEntry, Item, Tag;

class ServiceForm(forms.Form):
	CHOICES = (
		('A', 'Approve for Disbursment'),
		('L', 'Approve for Loan'),
		('B', 'Approve for Backfill'),
		('D', 'Deny'),
		);
	admin_comment = forms.CharField(max_length=200, required=False);
	approve_deny = forms.ChoiceField(widget=forms.RadioSelect, \
		choices=CHOICES);

def generate_choices(db_Model, data_display_field):
	print('in generate choices')
	CHOICES = (());
	first = True;
	for instance in db_Model.objects.all():
		if first:
			CHOICES = ((instance.pk, getattr(instance, data_display_field)),);
			first = False;
			continue;
		CHOICES = CHOICES + ((instance.pk, getattr(instance, data_display_field)),);
	return CHOICES;

# tag handling forms
class TagModifyForm(forms.Form):
	old_name = forms.CharField(max_length=100);
	new_name = forms.CharField(max_length=100);

# @deprecated
class TagCreateForm(forms.Form):
	current_items = Item.objects.all();

	ITEMS = generate_choices(Item, 'item_name');

	new_tag_name = forms.CharField(max_length=100, label = "Tag Name");
	tagged_items = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, \
		required=False, choices=ITEMS, label="Tag Some Items");

	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		ITEMS = generate_choices(Item, 'item_name');
		self.fields['tagged_items'].choices=ITEMS;

# @deprecated
class TagDeleteForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		TAGS = generate_choices(Tag, 'tag');
		self.fields['to_delete'].choices=TAGS;

	TAGS = generate_choices(Tag, 'tag');
	to_delete = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
		choices=TAGS, label="Tags to Delete")

# the item form; complicated by custom fields
def ItemForm_init(self, *args, **kwargs):
	super(self.__class__, self).__init__(*args, **kwargs)
	#TAGS = generate_choices(Tag, 'tag');
	#self.fields['tags'].choices=TAGS;



def AssetForm_factory(asset_tag):
	properties = dict();
	properties['asset_tag'] = forms.IntegerField(initial=asset_tag);

	custom_fields = CustomFieldEntry.objects.filter(per_asset=True);
	for cf in custom_fields:
		field_name = cf.field_name;
		field_type = cf.value_type;
		print(field_name);
		if field_type == 'st':
			properties[field_name] = forms.CharField(max_length=100, required=False)
		elif field_type == 'lt':
			properties[field_name] = forms.CharField(widget=forms.Textarea, required=False);
		elif field_type == 'int':
			properties[field_name] = forms.IntegerField(required=False);
		elif field_type == 'float':
			properties[field_name] = forms.FloatField(required=False);

	# use python's magic 'type' method to create a class
	return type('AssetForm', (forms.Form,), properties);

# takes two keyword arguments "item_type" and "is_asset_row"
# item_type is either "Item" or "Asset" and alters the form accordingly
# is_asset_row is True/False, and whether or not it's an Item that represents assets
def ItemForm_factory(**kwargs):

	TAGS = generate_choices(Tag, 'tag');

	if kwargs['item_type'] == 'Asset':
		count_field = forms.IntegerField(min_value=0, max_value=1);
	else:
		count_field = forms.IntegerField(min_value=0);

	print('tags: ');
	print(TAGS);
	#TAGS = (('1', 'pick 1'), ('2', 'pick 2'));
	# class variables of the ItemForm class for which this is a factory
	properties = {
		'item_name': forms.CharField(max_length=100),
		'model_number': forms.CharField(max_length=100, required=False),
		'description': forms.CharField(widget=forms.Textarea, required=False),
		'count': count_field,
		'minimum_stock': forms.IntegerField(min_value=0, required=False),
		#'tags': forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, \
		#	choices=TAGS, required=False),
		'__init__': ItemForm_init,
	}

	# add more class variables to properties for the custom fields
	if kwargs['item_type'] == 'Asset':
		custom_fields = CustomFieldEntry.objects.filter(per_asset=True);
	elif kwargs['is_asset_row']:
		custom_fields = CustomFieldEntry.objects.filter(per_asset=False);
	else:
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
			properties[field_name] = forms.IntegerField(required=False);
		elif field_type == 'float':
			properties[field_name] = forms.FloatField(required=False);

	# use python's magic 'type' method to create a class
	return type('ItemForm', (forms.Form,), properties);


# add or remove custom fields
class CFAddForm(forms.Form):
	TYPES = (('lt', 'Long Text'), ('st', 'Short Text'), \
		('int', 'Integer'), ('float', 'Float'));
	PRIV = ((True, 'Private'), (False, 'Not Private'));
	value_type = forms.ChoiceField(widget=forms.RadioSelect, choices=TYPES);
	field_name = forms.CharField(max_length=100);
	is_private = forms.ChoiceField(widget=forms.RadioSelect, choices=PRIV);

class PositiveIntArgMaxForm(forms.Form):
	def __init__(self, *args, **kwargs):
		max_val = kwargs.pop('max_val');
		super(self.__class__, self).__init__(*args, **kwargs)
		#print(kwargs['max_val'])
		self.fields['Amount'] = forms.IntegerField(min_value=1, max_value=max_val)
		self.fields['Comment'] = forms.CharField(initial='No Comment', required=False);
