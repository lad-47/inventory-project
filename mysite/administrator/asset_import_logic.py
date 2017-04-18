import json
from home.models import Asset,Item,Tag,CustomFieldEntry,CustomIntField,CustomFloatField,CustomLongTextField,CustomShortTextField
from manager.auto_increment import generateAssetTag

def import_asset_data(raw):
    """ This function parses JSON data and attempts to import asset instances into the system.
        Output: a status string which is either:
            - 'OK': Data was imported and saved to the database
            - otherwise, the function returns an error message
    """
    if not raw or raw == "":
        return "Format: Please enter some text."
    try:
        assets = create_objs_from_json(raw)
    except ValueError:
        return "Format: Please format JSON correctly."
    #print(str(items))
    status = check_valid_assets(assets)
    if status == "OK":
        save_assets(assets)
    return status

def create_objs_from_json(asset_json):
    # Returns a list of objs from json input
    objs = json.loads(asset_json)
    return objs

def check_valid_assets(assets_from_json):
    # If one item is not valid, the whole import fails
    for asset in assets_from_json:
        asset_is_valid = valid(asset)
        if asset_is_valid != "OK":
            return asset_is_valid
    #print("All Assets Valid.")
    return "OK"

def valid(asset):
    """ Checks if an asset instance is valid """
    keys = []
    for key,value in asset.items():
        keys.append(key)
        if key == 'asset_name':
            name_is_valid = valid_name(value)
            if name_is_valid != 'OK':
                print("Name is not valied.")
                return name_is_valid
        elif key == 'custom_fields':
            cfs_is_valid = valid_customs(value)
            if cfs_is_valid != 'OK':
                print("CFs are not valied.")
                return cfs_is_valid
        else:
            return "Format: Illegal JSON key name. Accepted tags are: "+\
                    "asset_name, custom_fields."
    if not 'asset_name' in keys:
        return "Format: Asset instances need an asset_name."
    return "OK"

def valid_name(name):
    if not isinstance(name, str):
        return "Format: item_name should be a str."
    # An item needs a name
    if not name or name == "":
        return "Format: User needs to provide a value for asset_name."
    else:
        # Check to make sure an item with that name exists!
        try:
            existing_item = Item.objects.get(item_name=name)
        except Item.DoesNotExist:
            return "An asset with the name "+name+" needs to be created before "+\
                    "you can add instances of it."
    #print("Name "+name+" is valid.")
    return "OK"

def valid_customs(custom_fields):
    if not isinstance(custom_fields, list):
        return "Format: Custom fields should be in a list."
    for cf in custom_fields:
        cf_name = cf['field_name']
        cf_value = cf['field_value']
        try:
            existing_cf = CustomFieldEntry.objects.get(field_name=cf_name)
        except CustomFieldEntry.DoesNotExist:
            return "Error: Custom field, "+cf_name+", does not exist."
        if not existing_cf.per_asset:
            return "Format: Assets can only be associated with per-asset custom fields. "+cf_name
        field_type = existing_cf.value_type
        if field_type == "st":
            # Short Text
            if not isinstance(cf_value, str):
                return "Format: Short text field should be of type str."
        elif field_type == "lt":
            # Long Text
            if not isinstance(cf_value, str):
                return "Format: Long text field should be of type str."
        elif field_type == "int":
            # Integer
            if not isinstance(cf_value, int):
                return "Format: Integer field should be of type int."
        elif field_type == "float":
            # Float
            if not isinstance(cf_value, float):
                return "Format: Float field should be of type float."
        else:
            return "Database has been corrupted. An unexpected Custom Field"+\
                " type was encountered: CustomFieldEntry.field_type is illegal."
    return "OK"

def save_assets(assets):
    for asset in assets:
        name = asset['asset_name']
        try:
            item_instance = Item.objects.get(item_name=name)
        except Item.DoesNotExist:
            return "Error: Could not save asset "+name+", an item with a matching name was not found."
        asset_instance = Asset.objects.create(asset_tag=generateAssetTag(),\
                            item_name=asset['asset_name'],count=1,\
                            model_number=item_instance.model_number,\
                            description=item_instance.description, is_asset=True)

        for tag in item_instance.tags.all():
            asset_instance.tags.add(tag)
        asset_instance.save()
        cfs = asset.get('custom_fields',[])
        for cf in cfs:
            cf_name = cf['field_name']
            cf_value = cf['field_value']
            for field_entry in CustomFieldEntry.objects.filter(per_asset=True):
                if cf_name == field_entry.field_name:
                    field_type = field_entry.value_type
                    if field_type == "st":
                        new_cf = CustomShortTextField.objects.create(\
                                    parent_item=item_instance,\
                                    field_name=field_entry, field_value = cf_value)
                        new_cf.save();
                    elif field_type == "lt":
                        new_cf = CustomLongTextField.objects.create(\
                                    parent_item=item_instance,\
                                    field_name=field_entry, field_value = cf_value)
                        new_cf.save();
                    elif field_type == "int":
                        new_cf = CustomIntField.objects.create(\
                                    parent_item=item_instance,\
                                    field_name=field_entry, field_value = cf_value)
                        new_cf.save();
                    elif field_type == "float":
                        new_cf = CustomFloatField.objects.create(\
                                    parent_item=item_instance,\
                                    field_name=field_entry, field_value = cf_value)
                        new_cf.save();
