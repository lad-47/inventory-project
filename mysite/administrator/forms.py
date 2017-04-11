from django import forms
from home.models import CustomFieldEntry, Item, Tag;


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

# add or remove custom fields
class CFAddForm(forms.Form):
	TYPES = (('lt', 'Long Text'), ('st', 'Short Text'), \
		('int', 'Integer'), ('float', 'Float'));
	PRIV = ((True, 'Private'), (False, 'Not Private'));
	PER_ASSET = ((True, 'Track Per Asset'), (False, "Don't Track Per Asset"));
	
	field_name = forms.CharField(max_length=100, label="Field Name");
	value_type = forms.ChoiceField(widget=forms.RadioSelect, choices=TYPES, label="Field Datatype");
	is_private = forms.ChoiceField(widget=forms.RadioSelect, choices=PRIV, label="Field Privacy");
	is_private = forms.ChoiceField(widget=forms.RadioSelect, choices=PER_ASSET, label="Per asset field?");


class CFDeleteForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		CFs = generate_choices(CustomFieldEntry, 'field_name');
		self.fields['to_delete'].choices=CFs;

	CFs = generate_choices(CustomFieldEntry, 'field_name');
	to_delete = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, \
		choices=CFs, label="Custom Fields to Delete");

