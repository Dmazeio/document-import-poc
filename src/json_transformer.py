# File: src/json_transformer.py (UPDATED VERSION WITH ATTENDEES SUPPORT)

import uuid
from .tools import find_user_id_by_name, find_user_ids_from_text  # Import both lookup functions

def flatten_recursively(data_node: dict, schema_node: dict, parent_id: str, parent_type: str, flat_list: list, entity_map: dict):
    
    object_name = schema_node['name']
    
    node_id = f"{object_name}-{uuid.uuid4()}"
    dmaze_object = { "id": node_id, "objectname": object_name }
    if parent_id:
        dmaze_object["parentid"] = parent_id
        dmaze_object["parenttype"] = parent_type

    for field_info in schema_node['fields']:
        field_name = field_info['fieldname']
        entity_key = field_info.get('entitytype')
        ai_value = data_node.get(field_name)

        # === ENHANCED HYBRID LOGIC ===
        if field_name == 'e_attendees_ids' and entity_key == 'people':
            # Special handling for attendees field - parse multiple names
            user_ids = find_user_ids_from_text(ai_value) if ai_value else []
            if user_ids:
                dmaze_object[field_name] = {
                    "type": "user",
                    "values": user_ids  # Already a list
                }
            else:
                dmaze_object[field_name] = None
        elif entity_key == 'user':
            # Single user field (like e_responsible_ids)
            user_id = find_user_id_by_name(ai_value)
            if user_id:
                dmaze_object[field_name] = {
                    "type": "user",
                    "values": [user_id]  # Single ID in a list
                }
            else:
                dmaze_object[field_name] = None
        elif entity_key and ai_value is not None:
            # For all OTHER entities (like 'momstatus'), use the entity_map method
            final_value = entity_map.get(entity_key, {}).get(ai_value, ai_value) 
            dmaze_object[field_name] = final_value
        else:
            # For regular fields, use the value as is
            dmaze_object[field_name] = ai_value
    
    for child_schema in schema_node.get('children', []):
        child_name = child_schema['name']
        child_items = data_node.get(child_name, [])
        child_ids = []
        
        if child_items:
            for item in child_items:
                # IMPORTANT: Pass entity_map recursively
                child_id = flatten_recursively(item, child_schema, node_id, object_name, flat_list, entity_map)
                child_ids.append(child_id)
        
        relationship_field = child_schema['relationship_field']
        dmaze_object[relationship_field] = { "type": child_name, "values": child_ids }

    flat_list.append(dmaze_object)
    return node_id

def transform_to_dmaze_format_hierarchically(nested_data: dict, schema_package: dict) -> list:
    final_list = []
    schema_tree = schema_package['schema_tree']
    entity_map = schema_package.get('entity_map', {})
    root_name = schema_tree['name']

    if root_name not in nested_data:
        return [{"error": f"Input from AI is missing the root key '{root_name}'."}]

    flatten_recursively(
        data_node=nested_data[root_name],
        schema_node=schema_tree,
        parent_id=None,
        parent_type=None,
        flat_list=final_list,
        entity_map=entity_map
    )

    root_index = next((i for i, obj in enumerate(final_list) if obj.get('objectname') == root_name), -1)
    if root_index != -1:
        root_obj = final_list.pop(root_index)
        final_list.insert(0, root_obj)

    return final_list