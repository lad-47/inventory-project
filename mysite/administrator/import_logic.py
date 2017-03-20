import json

def import_data(raw):
    items = create_items_from_json(raw)
    print(str(items))
    status = check_valid_items(items)
    if status == 'valid':
        # TODO: Save the items to the database and let the user know
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
    if not check_name_conflicts(items_from_json):
        return False
    # If one item is not valid, the whole import fails
    for item in items:
        if not valid_item(item):
            return False

def valid_item(item):
    """ checks if a single item is valid """
    # An item needs a name
    if not item['item_name']:
        return False
    else:
        # TODO: check to make sure an item with that name does not already exist!
        return True

    # Check positive count
    if item['count'] < 0:
        return False

    # Check tags
    if item['tags']:
        for tag in item['tags']:
            # TODO: check to make sure the tag exists
            # if tag DNE, create the tag
            continue

    # Custom Fields
    # these should be contained within the list "custom_fields",
    # and should have "name" and "value"
    if item['custom_fields']:
        for cf in item['custom_fields']:
            # TODO: Check name exists
            # Make sure type matches
            continue

    return True

def check_name_conflicts(items):
    """ checks unique names have been given in the input data """
    # TODO: fix logic!!!!!!!!!!! needs to look specifically at "item_name"
    counts = {}
    for i in range(len(items)):
        for item in items[i]:
            if not counts[item]:
                counts[item] = {}
            if not counts[item][items[i][item]]:
                counts[item][items[i][item]] = 0
            counts[item][items[i][item]] = counts[item][items[i][item]]+1
    for name in counts:
        if counts[name] > 1:
            return False
    return True
