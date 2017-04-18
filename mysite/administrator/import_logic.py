import json
from home.models import Item,Tag,CustomFieldEntry,CustomIntField,CustomFloatField,CustomLongTextField,CustomShortTextField

def import_data(raw):
    """ This function parses JSON data and attempts to import items into the system.
        Output: a status string which is either:
            - 'OK': Data was imported and saved to the database
            - otherwise, the function returns an error message
    """
    if not raw or raw == "":
        return "Format: Please enter some text."
    try:
        items = create_items_from_json(raw)
    except ValueError:
        return "Format: Please format JSON correctly."
    #print(str(items))
    status = check_valid_items(items)
    if status == "OK":
        save_items(items)
    return status

def create_items_from_json(json_items):
    # Returns a list of items from json input
    items = json.loads(json_items)
    return items

def check_valid_items(items_from_json):
    # If more than one item with the same name is input, import fails
    name_is_valid = check_name_conflicts(items_from_json)
    if not name_is_valid == "OK":
        #print("Name conflicts occurred when checking input.")
        return name_is_valid
    # If one item is not valid, the whole import fails
    for item in items_from_json:
        item_is_valid = valid_item(item)
        if item_is_valid != "OK":
            return item_is_valid
    #print("All Items Valid.")
    return "OK"

def check_name_conflicts(items):
    """ checks unique names have been given in the input data, if not an asset """
    counts = {}
    item_set = set()
    asset_set = set()
    for i in range(len(items)):
        item = items[i]
        # item holds a loaded json object
        if not item.get('asset_name',None):
            if item.get('item_name',None):
                name = item['item_name']
                if name not in item_set:
                    item_set.add(name)
                else:
                    return "Found duplicate item name "+name+" in JSON input."
            else:
                return "Format: item JSON data needs an 'item_name' field"
        else:
            if item.get('asset_name',None):
                name = item['asset_name']
                if name not in asset_set:
                    asset_set.add(name)
                # if name not in item_set:
                #     return "Format: Tried to add an asset instance of "+name+" but "+\
                #             "an asset row does not exist for that Item."
    for asset_name in asset_set:
        if asset_name not in item_set:
            # Check to make sure an item with that name exists!
            try:
                existing_item = Item.objects.get(item_name=asset_name)
            except Item.DoesNotExist:
                return "Format: Tried to add an asset instance of "+name+" but "+\
                        "an asset row does not exist for that Item."
    return "OK"

def valid_item(item, items):
    """ checks if a single item is valid """
    keys = []
    isAsset = item.get('is_asset', False)
    assetName = item.get('asset_name', None)
    itemName = item.get('item_name',None)
    name = ''
    if item.get('item_name',None):
        name = item['item_name']
    elif item.get('asset_name',None):
        name = item['asset_name']
    else:
        return "Format: item_name or asset_name must be provided."
    if isAsset and assetName:
        return "Format: an item with is_asset=true should have item_name, not asset_name."
    elif assetName and itemName:
        return "Format: Please specify only one of the following fields for item "+name+\
                ": item_name, asset_name."
    elif not isAsset and not assetName:
        # Item is not an Asset, validate normally
        valid_normal_item = help_valid_item(item)
        if valid_normal_item != "OK":
            return valid_normal_item
    elif isAsset and itemName:
        # Item is an Asset
        valid_item_asset = help_valid_item_asset(item)
        if valid_item_asset != "OK":
            return valid_item_asset
    elif assetName:
        # This is an Asset instance
        valid_asset = help_valid_asset(item, items)
        if valid_asset != "OK":
            return valid_asset
    else:
        return "Format: Item "+name+" formatted incorrectly."
    return "OK"

def help_valid_item(item):
    is_asset = item.get('is_asset', False)
    keys = []
    for key,value in item.items():
        keys.append(key)
        if key == 'item_name':
            name_is_valid = valid_name(value)
            #print(str(name_is_valid))
            if name_is_valid != "OK":
                return name_is_valid
        elif key == 'count':
            count_is_valid = valid_count(value)
            if not count_is_valid == "OK":
                return count_is_valid
        elif key == 'model_number':
            if not isinstance(value, str):
                return "Format: Item model_number should be a str."
        elif key == 'description':
            if not isinstance(value, str):
                return "Format: Item description should be a str."
        elif key == 'tags':
            tags_is_valid = valid_tags(value)
            if not tags_is_valid == "OK":
                return tags_is_valid
        elif key == 'custom_fields':
            cfs_is_valid = valid_customs(value,is_asset)
            if not cfs_is_valid == "OK":
                return cfs_is_valid
        elif key == 'is_asset':
            if value:
                return "Format: Item "+item.get('item_name','[could not find item name]')+\
                        " should not have is_asset=true."
        else:
            return "Format: Illegal JSON key name. Accepted tags are: "+\
                    "item_name, count, model_number, description, is_asset, tags, and custom_fields."
    if not 'item_name' and not 'count' in keys:
        return "Format need count in JSON item data."
    return "OK"

def help_valid_item_asset(item):
    keys = []
    for key,value in item.items():
        keys.append(key)
        if key == 'item_name':
            name_is_valid = valid_name(value)
            if name_is_valid != "OK":
                return name_is_valid
        elif key == 'model_number':
            if not isinstance(value, str):
                return "Format: Item model_number should be a str."
        elif key == 'description':
            if not isinstance(value, str):
                return "Format: Item description should be a str."
        elif key == 'tags':
            tags_is_valid = valid_tags(value)
            if not tags_is_valid == "OK":
                return tags_is_valid
        elif key == 'custom_fields':
            cfs_is_valid = valid_customs(value,True)
            if not cfs_is_valid == "OK":
                return cfs_is_valid
        elif key == 'is_asset':
            # value should be true
            pass
        else:
            return "Format: Illegal JSON key name. Accepted tags for Item/Assets are: "+\
                    "item_name, model_number, description, is_asset, tags, and custom_fields."
    if not 'item_name' in keys:
        return "Format: need count in JSON item data."
    if 'count' in keys:
        return "Format: do not include a count for Asset Items."
    return "OK"

def help_valid_asset(item, items):
    keys = []
    for key,value in item.items():
        keys.append(key)
        if key == 'asset_name':
            asset_name_valid = valid_asset_name(value, items)
            if asset_name_valid != "OK":
                return asset_name_valid
        elif key == 'custom_fields':
            asset_cf_valid = valid_cfs_asset(value)
            if asset_cf_valid != "OK":
                return asset_cf_valid
        else:
            return "Format: Illegal JSON key name. Accepted tags for Assets are: "+\
                    "asset_name, custom_fields."

def valid_asset_name(name, items):
    try:
        item_instance = Item.objects.get(item_name=name)
        if not item_instance.is_asset:
            return "Format: Item with name "+name+" is not an Asset."
    except:
        asset_row_in_input = False
        for item in items:
            if item.get('item_name',None) == name:
                asset_row_in_input = True
                break
        if not asset_row_in_input:
            return "An Item with name "+name+" does not exist. Please create an "+\
                    "item instance with this name before trying to create Asset instances."
    return "OK"

def valid_cfs_asset(custom_fields):
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

def valid_name(name):
    if not isinstance(name, str):
        return "Format: item_name should be a str."
        # An item needs a name
        if not name or name == "":
            return "Format: User needs to provide a value for 'item_name'."
        else:
            # Check to make sure an item with that name does not already exist!
            try:
                existing_item = Item.objects.get(item_name=name)
                return "An item with name, "+name+", already exists!"
            except Item.DoesNotExist:
                pass
    #print("Name "+name+" is valid.")
    return "OK"

def valid_count(count):
    # Check positive count
    if not isinstance(count, int):
        return "Format: Item count should be an int."
    if not count:
        return "Format: User needs to provide a count"
    if count < 0:
        return "Format: An item count was negative."
    #print("Count is Valid.")
    return "OK"

def valid_tags(tags):
    if not isinstance(tags, list):
        return "Format: Item tags should be in a list."
    # Check tags
    for tag in tags:
        # if tag DNE, create it
        tag_name = tag.get('tag',None)
        if tag_name:
            try:
                existing_tag = Tag.objects.get(tag=tag_name)
                #print("Tag "+tag_name+" was found.")
            except Tag.DoesNotExist:
                new_tag = Tag.objects.create(tag=tag_name)
                #print("Tag "+tag_name+" was created!")
        else:
            return "Format: User needs to provide tag name."
    return "OK"

def valid_customs(custom_fields, is_asset):
    if not isinstance(custom_fields, list):
        return "Format: Custom fields should be in a list."
    # Should have "field_name" and "field_value". Reject non-existing CFs.
    for cf in custom_fields:
        # Check name exists. Make sure type matches
        cf_name = cf['field_name']
        cf_value = cf['field_value']
        try:
            existing_cf = CustomFieldEntry.objects.get(field_name=cf_name)
            if is_asset and existing_cf.per_asset:
                return "Format: Only non-per-asset custom fields can be specified for an asset item instance. "+cf_name
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
        except CustomFieldEntry.DoesNotExist:
            return "Error: Custom field, "+cf_name+", does not exist."
    return "OK"

def save_items(items):
    print("Saving Items...")
    for item in items:
        if item.get('item_name',None):
            # Item instance
            if item.get('is_asset',False):
                # Item/Asset initialized to count=0
                item_asset_count = 0
                item_instance = Item(item_name=item['item_name'], name_unique_check=item['item_name'],\
                    model_number=item.get('model_number',""),is_asset=True,\
                    description=item.get('description',""), count=item_asset_count)
            else:
                # Create the item_instance, cfs, and tags, with save()
                item_instance = Item(item_name=item['item_name'], name_unique_check=item['item_name'],\
                    model_number=item.get('model_number',""),is_asset=False,\
                    description=item.get('description',""), count=item['count'])
            # Attempt to save item instance
            try:
                item_instance.save()
            except:
                return "Item with name "+item['item_name']+" failed to save correctly."
            # Create cfs
            if item.get('custom_fields',None):
                save_cfs(item['custom_fields'],item_instance)
            # Create non-existing tags.
            if item.get('tags',None):
                for tag_name in item['tags']:
                    try:
                        item_instance.tags.add(Tag.objects.get(tag=tag_name['tag']))
                    except Tag.DoesNotExist:
                        # Create new tag
                        new_tag = Tag.objects.create(tag=tag_name)
                        new_tag.save()
                        item_instance.tags.add(new_tag)
            # # Create item instance
            # try:
            #     item_instance.save()
            # except:
            #     return "Item with name "+item['item_name']+" failed to save correctly."
        else:
            #Asset instance
            asset_instance = Asset(item_name=item['asset_name'],asset_tag=generateAssetTag(),\
                                    model_number=item.get('model_number',''),is_asset=True,\
                                    description=item.get('description',''),count=1)
            try:
                asset_instance.save()
            except:
                return "Asset with name "+item['item_name']+" failed to save correctly."
            if item.get('custom_fields',None):
                save_cfs(item['custom_fields'],asset_instance)

def save_cfs(custom_fields, item_instance):
    for cf in custom_fields:
        cf_name = cf['field_name']
        cf_value = cf['field_value']
        for field_entry in CustomFieldEntry.objects.all():
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
