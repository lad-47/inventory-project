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

def valid_item(item):
    """ checks if a single item is valid """
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
            cfs_is_valid = valid_customs(value)
            if not cfs_is_valid == "OK":
                return cfs_is_valid
        else:
            return "Format: Illegal JSON key name. Accepted tags are: "+\
                    "item_name, count, model_number, description, tags, and custom_fields."
    #print(str(keys))
    if not 'item_name' in keys or not 'count' in keys:
        return "Format: Need item_name and count in JSON item data."
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

def valid_customs(custom_fields):
    if not isinstance(custom_fields, list):
        return "Format: Custom fields should be in a list."
    # Should have "field_name" and "field_value". Reject non-existing CFs.
    for cf in custom_fields:
        # Check name exists. Make sure type matches
        cf_name = cf['field_name']
        cf_value = cf['field_value']
        try:
            existing_cf = CustomFieldEntry.objects.get(field_name=cf_name)
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

def check_name_conflicts(items):
    """ checks unique names have been given in the input data """
    counts = {}
    item_set = set()
    for i in range(len(items)):
        item = items[i]
        if item.get('item_name',None):
            name = item['item_name']
            if name not in item_set:
                item_set.add(name)
            else:
                return "Found duplicate item name "+name+" in JSON input."
        else:
            return "Format: item JSON data needs an 'item_name' field"
    return "OK"

def save_items(items):
    for item in items:
        # Create the item_instance, cfs, and tags, with save()
        item_instance = Item(item_name=item['item_name'],\
            model_number=item.get('model_number',""),\
            description=item.get('description',""), count=item['count'])
        # Create cfs
        if item.get('custom_fields',None):
            save_cfs(item['custom_fields'],item_instance)
        # Attempt to save item instance
        try:
            item_instance.save()
        except:
            return "Item with name "+item['item_name']+" failed to save correctly."
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
        # Create item instance
        try:
            item_instance.save()
        except:
            return "Item with name "+item['item_name']+" failed to save correctly."

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
                                field_name=cf_nfield_entryame, field_value = cf_value)
                    new_cf.save();
                elif field_type == "float":
                    new_cf = CustomFloatField.objects.create(\
                                parent_item=item_instance,\
                                field_name=field_entry, field_value = cf_value)
                    new_cf.save();
