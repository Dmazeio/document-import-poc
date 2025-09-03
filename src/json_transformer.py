# File: src/json_transformer.py

import uuid

def transform_to_dmaze_format_dynamically(nested_data: dict, schema_metadata: dict) -> list:
    """
    Transforms the nested JSON into the Dmaze format using
    metadata from the template. This code is now agnostic to field names.
    """
    # 1. Get the names from the metadata (the recipe)
    parent_name = schema_metadata['parent_name']
    child_name = schema_metadata['child_name']
    relationship_field = schema_metadata['relationship_field']

    # Check if the data from the AI matches what we expect from the metadata
    if parent_name not in nested_data or child_name not in nested_data:
        return [{"error": "Input from AI is missing parent or child keys defined in the schema."}]

    flat_list = []
    parent_data = nested_data.get(parent_name, {})
    child_items = nested_data.get(child_name, [])

    # 2. Generate a unique ID for the parent
    parent_id = f"{parent_name}-{uuid.uuid4()}"
    child_ids = []
    
    # 3. Build all the child objects
    for item in child_items:
        child_id = f"{child_name}-{uuid.uuid4()}"
        child_ids.append(child_id)
        
        child_object = {
            "id": child_id,
            "parentid": parent_id,
            "parenttype": parent_name,
            "objectname": child_name
        }
        # Copy all data fields dynamically
        for field in schema_metadata['child_fields']:
            child_object[field] = item.get(field)
        flat_list.append(child_object)

    # 4. Build the parent object
    parent_object = {
        "id": parent_id,
        "objectname": parent_name,
        relationship_field: {
            "type": child_name,
            "values": child_ids
        }
    }
    # Copy all data fields dynamically
    for field in schema_metadata['parent_fields']:
        parent_object[field] = parent_data.get(field)

    # Insert the parent at the beginning of the list
    flat_list.insert(0, parent_object)

    return flat_list