import json
from home.models import Item,CustomFieldEntry

def import_data(raw):
    """ This function parses JSON data and attempts to import items into the system.
        Output: a status string which is either:
            - 'OK': Data was imported and saved to the database
            - otherwise, the function returns an error message
    """
    items = create_items_from_json(raw)
    print(str(items))
    status = check_valid_items(items)
    if status == 'valid':
        # TODO: Save the items to the database and let the user know
        save_items(items)
        return True
    elif status == True:
        # A bit messy currently due to the discrepancy between returning useful
        # feedback vs. simply True/False....CHANGE!
        save_items(items)
        return True
    else:
        # TODO: Return useful feedback to user depending on what went wrong
        return False

def create_items_from_json(json_items):
    # Returns a list of items from json input
    items = json.loads(json_items)
    return items

def check_valid_items(items_from_json):
    # If more than one item with the same name is input, import fails
    name_is_valid = check_name_conflicts(items_from_json)
    if not name_is_valid == "OK":
        print("Name conflicts occurred when checking input.")
        return name_is_valid
    # If one item is not valid, the whole import fails
    for item in items_from_json:
        if not valid_item(item):
            print("An item entered was not valid. "+str(item))
            return False
    print("All Items Valid.")
    return True

def save_items(items):
    for item in items:
        # Create the item_instance, cfs, and tags, with save()
        item_instance = Item(item_name=item['item_name'],\
            model_number=item.get('model_number',""),\
            description=item.get('description',""), count=item['count'])
        # Create cfs
        if item.get('custom_fields',None):
            save_cfs(item['custom_fields'])
        # Create non-existing tags.
        if item.get('tags',None):
            for tag_name in item['tags']:
                try:
                    item_instance.tags.add(Tag.objects.get(tag=tag_name))
                except Tag.DoesNotExist:
                    # Create new tag
                    new_tag = Tag.objects.create(tag=tag_name)
                    new_tag.save()
                    item_instance.tags.add(new_tag)
        # Create item instance
        item_instance.save()

def save_cfs(custom_fields):
    for cf in custom_fields:
        cf_name = cf['field_name']
        cf_value = cf['field_value']
        for field_entry in CustomFieldEntry.objects.all():
            if cf_name == field_entry.field_name:
                field_type = field_entry.value_type
                if field_type == "st":
                    new_cf = CustomShortTextField.objects.create(\
                                parent_item=item_instance,\
                                field_name=cf_name, field_value = cf_value)
                    new_cf.save();
                elif field_type == "lt":
                    new_cf = CustomLongTextField.objects.create(\
                                parent_item=item_instance,\
                                field_name=cf_name, field_value = cf_value)
                    new_cf.save();
                elif field_type == "int":
                    new_cf = CustomIntField.objects.create(\
                                parent_item=item_instance,\
                                field_name=cf_name, field_value = cf_value)
                    new_cf.save();
                elif field_type == "float":
                    new_cf = CustomFloatField.objects.create(\
                                parent_item=item_instance,\
                                field_name=cf_name, field_value = cf_value)
                    new_cf.save();

def valid_item(item):
    """ checks if a single item is valid """
    keys = []
    for key,value in item.items():
        keys.append(key)
        if key == 'item_name':
            if not valid_name(value):
                return False
        elif key == 'count':
            if not valid_count(value):
                return False
        elif key == 'model_number':
            if not isinstance(value, str):
                print("Format: Item model number should be a str.")
                return False
        elif key == 'description':
            if not isinstance(value, str):
                print("Format: Item description should be a str.")
                return False
        elif key == 'tags':
            if not valid_tags(value):
                return False
        elif key == 'custom_fields':
            if not valid_customs(value):
                return False
        else:
            print("Format: Illegal JSON key name.")
            return False
    print(str(keys))
    if not 'item_name' in keys or not 'count' in keys:
        print("Format: Need item_name and count in JSON")
        return False
    return True

def valid_name(name):
    if not isinstance(name, str):
        print("Format: Item name should be a str.")
        return False
    # An item needs a name
    if not name or name == "":
        return False
    else:
        # Check to make sure an item with that name does not already exist!
        try:
            existing_item = Item.objects.get(item_name=name)
            print("An item with name, "+name+", already exists!")
            return False
        except Item.DoesNotExist:
            pass
    return True

def valid_count(count):
    # Check positive count
    if not isinstance(count, int):
        print("Format: Item count should be an int.")
        return False
    if not count:
        print("Format: Item needs a count")
        return False
    if count < 0:
        print("Format: An item count was negative.")
        return False
    print("Count is Valid.")
    return True

def valid_tags(tags):
    if not isinstance(tags, list):
        print("Format: Item tags should be in a list.")
        return False
    # Check tags
    for tag in tags:
        # if tag DNE, create it
        tag_name = tag['tag']
        try:
            existing_tag = Tag.objects.get(tag=tag_name)
        except Tag.DoesNotExist:
            new_tag = Tag.objects.create(tag=tag_name)
    return True

def valid_customs(custom_fields):
    if not isinstance(custom_fields, list):
        print("Format: Custom fields should be in a list.")
        return False
    # Should have "field_name" and "field_value". Reject non-existing CFs.
    for cf in custom_fields:
        # TODO: Check name exists
        # Make sure type matches
        cf_name = cf['field_name']
        cf_value = cf['field_value']
        try:
            existing_cf = CustomFieldEntry.objects.get(field_name=cf_name)
            field_type = existing_cf.value_type
            if field_type == "st":
                # Short Text
                if not isinstance(cf_value, str):
                    return False
            elif field_type == "lt":
                # Long Text
                if not isinstance(cf_value, str):
                    return False
            elif field_type == "int":
                # Integer
                if not isinstance(cf_value, int):
                    return False
            elif field_type == "float":
                # Float
                if not isinstance(cf_value, float):
                    return False
            else:
                print("Data integrity error. CustomFieldEntry.field_type is illegal in database.")
        except CustomFieldEntry.DoesNotExist:
            print("Error: Custom field, "+cf_name+", does not exist.")
            return False
    return True

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
            return "Data format incorrect: needs an item_name"
    return "OK"
