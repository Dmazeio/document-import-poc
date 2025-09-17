# File: src/json_transformer.py (FINAL, BATCH-OPTIMIZED VERSION)

import uuid
import re
import json
from openai import OpenAI
from .api_simulator import get_entities_from_api, get_entity_schema_from_api
from .tools import find_best_entity_matches_in_batch

# --- NY HJELPEFUNKSJON FOR Å SAMLE INN "ARBEID" ---
def collect_entities_to_match(data_node: dict, schema_node: dict, items_to_match: dict):
    """Recursively traverses the data and schema to find all unique text values that need an ID lookup."""
    for field_info in schema_node.get('fields', []):
        entity_type = field_info.get('entitytype')
        if entity_type:
            raw_text_value = data_node.get(field_info['fieldname'])
            if raw_text_value:
                if entity_type not in items_to_match:
                    items_to_match[entity_type] = set()
                
                texts = re.split(r'[,;\n]|(?:\s+og\s+)|(?:\s+and\s+)', str(raw_text_value)) if field_info.get('type') == "multivalue" else [str(raw_text_value)]
                for text in texts:
                    cleaned_text = text.strip()
                    if cleaned_text:
                        items_to_match[entity_type].add(cleaned_text)

    for child_schema in schema_node.get('children', []):
        child_items = data_node.get(child_schema['name'], [])
        for item in child_items:
            collect_entities_to_match(item, child_schema, items_to_match)


# --- MODIFISERT FOR Å BRUKE ET FERDIG OPPSLAGSKART ---
def flatten_recursively(client: OpenAI, data_node: dict, schema_node: dict, parent_id: str, parent_type: str, flat_list: list, id_lookup_map: dict):
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

        if entity_type:
            entity_schema = get_entity_schema_from_api(entity_type)
            if not entity_schema:
                dmaze_object[field_name] = {"type": entity_type, "values": []}
                continue

            found_ids = []
            if raw_text_value:
                texts_to_match = re.split(r'[,;\n]|(?:\s+og\s+)|(?:\s+and\s+)', str(raw_text_value)) if field_type == "multivalue" else [str(raw_text_value)]
                for text in texts_to_match:
                    cleaned_text = text.strip()
                    if cleaned_text:
                        # RASKT OPPSLAG I KARTET - INGEN AI-KALL HER!
                        found_id = id_lookup_map.get(entity_type, {}).get(cleaned_text)
                        if found_id:
                            found_ids.append(found_id)
            
            type_name = entity_schema.get('dmaze_format_wrapper') or entity_type
            values_list = found_ids
            if field_type in ["singlevalue", "entity"] and len(values_list) > 1:
                values_list = [values_list[0]]
            
            dmaze_object[field_name] = {"type": type_name, "values": values_list}

        else:
            dmaze_object[field_name] = raw_text_value if raw_text_value is not None else ""

    for child_schema in schema_node.get('children', []):
        child_name = child_schema['name']  # <-- LEGG TIL DENNE DEFINISJONEN
        child_items = data_node.get(child_name, []) # <-- BRUK VARIABELEN HER
        child_ids = []
        if child_items:
            for item in child_items:
                child_id = flatten_recursively(client, item, child_schema, node_id, object_name, flat_list, id_lookup_map)
                child_ids.append(child_id)
        
        relationship_field = child_schema['relationship_field']
        dmaze_object[relationship_field] = {"type": child_name, "values": child_ids}

    flat_list.append(dmaze_object)
    return node_id


# --- HOVEDFUNKSJONEN SOM NÅ ORKESTRERER ALT ---
def transform_to_dmaze_format_hierarchically(client: OpenAI, nested_data: dict, schema_package: dict) -> list:
    final_list = []
    schema_tree = schema_package['schema_tree']
    root_name = schema_tree['name']

    if root_name not in nested_data:
        return [{"error": f"Input from AI is missing the root key '{root_name}'."}]

    # --- STEG 1: SAMLE ALT ARBEID ---
    print("\n--- Step 4a: Collecting all entities to be matched... ---")
    items_to_match = {}
    collect_entities_to_match(nested_data[root_name], schema_tree, items_to_match)
    
    # --- STEG 2: HENT ALLE NØDVENDIGE "FASITER" FRA API ---
    valid_entities_map = {
        entity_type: get_entities_from_api(entity_type)
        for entity_type in items_to_match.keys()
    }

    # --- STEG 3: KJØR ETT ENESTE, STORT AI-KALL ---
    print("\n--- Step 4b: Finding all ID matches in a single batch call... ---")
    id_lookup_map = find_best_entity_matches_in_batch(client, items_to_match, valid_entities_map)

    # --- STEG 4: BYGG DEN ENDELIGE STRUKTUREN ---
    print("\n--- Step 4c: Transforming data using the lookup map... ---")
    flatten_recursively(
        client=client,
        data_node=nested_data[root_name],
        schema_node=schema_tree,
        parent_id=None,
        parent_type=None,
        flat_list=final_list,
        id_lookup_map=id_lookup_map # Send med det ferdige oppslagskartet
    )

    root_index = next((i for i, obj in enumerate(final_list) if obj.get('objectname') == root_name), -1)
    if root_index != -1:
        root_obj = final_list.pop(root_index)
        final_list.insert(0, root_obj)

    return final_list