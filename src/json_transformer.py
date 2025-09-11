# File: src/json_transformer.py (FINAL VERSION REPLACING NULL WITH EMPTY STRING)

import uuid
import re
from openai import OpenAI
from .api_simulator import get_entities_from_api, get_entity_schema_from_api
from .tools import find_best_entity_match_with_ai

def flatten_recursively(client: OpenAI, data_node: dict, schema_node: dict, parent_id: str, parent_type: str, flat_list: list):
    
    object_name = schema_node['name']
    node_id = f"{object_name}-{uuid.uuid4()}"
    dmaze_object = {"id": node_id, "objectname": object_name}
    if parent_id:
        dmaze_object["parentid"] = parent_id
        dmaze_object["parenttype"] = parent_type

    for field_info in schema_node['fields']:
        field_name = field_info['fieldname']
        raw_text_value = data_node.get(field_name)
        
        field_type = field_info.get('type')
        entity_type = field_info.get('entitytype')

        # Beregn 'final_value' først, med None som standard
        final_value = None

        if entity_type and raw_text_value and field_type in ["singlevalue", "multivalue", "entity"]:
            
            entity_schema = get_entity_schema_from_api(entity_type)
            if not entity_schema:
                print(f"  - WARNING: No metadata schema for type '{entity_type}'. Skipping.")
                continue

            valid_entities = get_entities_from_api(entity_type)
            if not valid_entities:
                print(f"  - WARNING: No entity data for type '{entity_type}'. Skipping.")
                continue

            display_field = entity_schema['primary_display_field']
            id_field = entity_schema['id_field']
            
            found_ids = []
            texts_to_match = re.split(r'[,;\n]|(?:\s+og\s+)|(?:\s+and\s+)', raw_text_value) if field_type == "multivalue" else [raw_text_value]
            
            for text_part in texts_to_match:
                cleaned_text = text_part.strip()
                if cleaned_text:
                    best_id = find_best_entity_match_with_ai(
                        client, cleaned_text, valid_entities, entity_type, display_field, id_field
                    )
                    if best_id:
                        found_ids.append(best_id)

            wrapper = entity_schema['dmaze_format_wrapper']
            if found_ids:
                if wrapper:
                    final_value = {"type": wrapper, "values": found_ids}
                elif field_type in ["singlevalue", "entity"]:
                    final_value = found_ids[0]
                else:
                    final_value = found_ids
        
        elif raw_text_value is not None:
             final_value = raw_text_value
            
        # Legg alltid til feltet i objektet. Hvis verdien er None,
        # erstatt den med en tom streng ("").
        dmaze_object[field_name] = final_value if final_value is not None else ""
            
    # Rekursjon for barn-objekter (relasjoner)
    for child_schema in schema_node.get('children', []):
        child_name = child_schema['name']
        child_items = data_node.get(child_name, [])
        child_ids = []
        if child_items:
            for item in child_items:
                child_id = flatten_recursively(client, item, child_schema, node_id, object_name, flat_list)
                child_ids.append(child_id)
        
        relationship_field = child_schema['relationship_field']
        # Vi vil alltid ha med relasjonsfelt, selv om de er tomme
        dmaze_object[relationship_field] = {"type": child_name, "values": child_ids}

    flat_list.append(dmaze_object)
    return node_id


def transform_to_dmaze_format_hierarchically(client: OpenAI, nested_data: dict, schema_package: dict) -> list:
    final_list = []
    schema_tree = schema_package['schema_tree']
    root_name = schema_tree['name']

    if root_name not in nested_data:
        return [{"error": f"Input from AI is missing the root key '{root_name}'."}]
    
    flatten_recursively(
        client=client,
        data_node=nested_data[root_name],
        schema_node=schema_tree,
        parent_id=None,
        parent_type=None,
        flat_list=final_list,
    )

    # Sørg for at rot-objektet alltid er først i listen
    root_index = next((i for i, obj in enumerate(final_list) if obj.get('objectname') == root_name), -1)
    if root_index != -1:
        root_obj = final_list.pop(root_index)
        final_list.insert(0, root_obj)

    return final_list