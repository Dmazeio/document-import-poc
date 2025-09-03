# File: src/json_transformer.py
import uuid

def flatten_recursively(data_node: dict, schema_node: dict, parent_id: str, parent_type: str, flat_list: list):
    """
    Recursively traverses the nested data and schema tree to produce a flat list
    of Dmaze-compatible objects.
    """
    object_name = schema_node['name']
    
    # 1. Create the object for the current node
    node_id = f"{object_name}-{uuid.uuid4()}"
    dmaze_object = {
        "id": node_id,
        "objectname": object_name
    }
    if parent_id:
        dmaze_object["parentid"] = parent_id
        dmaze_object["parenttype"] = parent_type

    # 2. Copy all data fields from the AI output
    for field in schema_node['fields']:
        dmaze_object[field] = data_node.get(field)
    
    # 3. Process all children
    for child_schema in schema_node.get('children', []):
        child_name = child_schema['name']
        child_items = data_node.get(child_name, [])
        child_ids = []
        
        if child_items: # Make sure we have child items to process
            for item in child_items:
                # The recursive call!
                child_id = flatten_recursively(item, child_schema, node_id, object_name, flat_list)
                child_ids.append(child_id)
        
        # Add the relationship link to the parent (current node)
        relationship_field = child_schema['relationship_field']
        dmaze_object[relationship_field] = {
            "type": child_name,
            "values": child_ids
        }

    # 4. Add the fully processed object to our master list
    flat_list.append(dmaze_object)
    
    # 5. Return the ID of the created object so the parent can link to it
    return node_id


def transform_to_dmaze_format_hierarchically(nested_data: dict, schema_tree: dict) -> list:
    """
    Transforms the nested JSON into the Dmaze format using the hierarchical schema tree.
    """
    final_list = []
    root_name = schema_tree['name']

    # Check if the AI output contains the root key
    if root_name not in nested_data:
        return [{"error": f"Input from AI is missing the root key '{root_name}' defined in the schema."}]

    # Start the recursive flattening process from the root node
    flatten_recursively(
        data_node=nested_data[root_name],
        schema_node=schema_tree,
        parent_id=None,
        parent_type=None,
        flat_list=final_list
    )

    # Re-order to ensure the parent (root) is the first element in the list
    root_index = next((i for i, obj in enumerate(final_list) if obj.get('objectname') == root_name), -1)
    if root_index != -1:
        root_obj = final_list.pop(root_index)
        final_list.insert(0, root_obj)

    return final_list