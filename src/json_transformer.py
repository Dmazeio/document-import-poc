import uuid
import re
from .ai_client import AIClient # Import AIClient
from .api_simulator import get_entities_from_api, get_entity_schema_from_api
from .tools import find_best_entity_matches_in_batch

def collect_entities_to_match(data_node: dict, schema_node: dict, items_to_match: dict):
    """Recursively traverses the data and schema to find all unique text values that need an ID lookup."""
    for field_info in schema_node.get('fields', []):
        entity_type = field_info.get('entitytype')
        if entity_type:
            raw_text_value = data_node.get(field_info['fieldname'])
            

            if raw_text_value is not None and str(raw_text_value).strip().lower() != "null":
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

def flatten_recursively(ai_client: AIClient, data_node: dict, schema_node: dict, parent_id: str, parent_type: str, flat_list: list, detailed_lookup_map: dict, warnings: list):
    """
    Recursively flattens the nested data into a list of Dmaze objects.
    It uses a detailed map to look up IDs and generates warnings for low-confidence matches.
    (Note: This function does not generate "not found" warnings itself; that's handled before it's called).
    """
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
            # If we have no detailed lookup data for this entity type, we may have
            # intentionally skipped matching (e.g., types like 'agenda' or 'measure').
            # In that case, preserve the raw text value instead of attempting ID lookup.
            if not detailed_lookup_map.get(entity_type):
                # Keep the original text (or empty string) so information is not lost
                dmaze_object[field_name] = raw_text_value if raw_text_value is not None else ""
            else:
                entity_schema = get_entity_schema_from_api(entity_type)
                if not entity_schema:
                    dmaze_object[field_name] = {"type": entity_type, "values": []}
                    continue

                found_ids = []
                if raw_text_value is not None and str(raw_text_value).strip().lower() != "null":
                    texts_to_match = re.split(r'[,;\n]|(?:\s+og\s+)|(?:\s+and\s+)', str(raw_text_value)) if field_type == "multivalue" else [str(raw_text_value)]
                    for text in texts_to_match:
                        cleaned_text = text.strip()
                        if cleaned_text:
                            match_details = detailed_lookup_map.get(entity_type, {}).get(cleaned_text)
                            if match_details:
                                found_id = match_details['id']
                                found_ids.append(found_id)
                                if match_details.get('confidence', 'High') in ["Medium", "Low"]:
                                    warning_msg = f"Low confidence match for '{cleaned_text}' (Type: {entity_type}): Matched to ID '{found_id}'. Reason: {match_details.get('reasoning', 'N/A')}"
                                    warnings.append(warning_msg)

                type_name = entity_schema.get('dmaze_format_wrapper') or entity_type
                values_list = found_ids
                if field_type in ["singlevalue", "entity"] and len(values_list) > 1:
                    values_list = [values_list[0]]

                dmaze_object[field_name] = {"type": type_name, "values": values_list}
        else:
            dmaze_object[field_name] = raw_text_value if raw_text_value is not None else ""

    for child_schema in schema_node.get('children', []):
        child_name = child_schema['name']
        child_items = data_node.get(child_name, [])
        child_ids = []
        if child_items:
            for item in child_items:
                child_id = flatten_recursively(ai_client, item, child_schema, node_id, object_name, flat_list, detailed_lookup_map, warnings)
                child_ids.append(child_id)
        
        relationship_field = child_schema['relationship_field']
        dmaze_object[relationship_field] = {"type": child_name, "values": child_ids}

    flat_list.append(dmaze_object)
    return node_id


# MAIN FUNCTION 
def transform_to_dmaze_format_hierarchically(ai_client: AIClient, nested_data: dict, schema_package: dict) -> dict:
    final_list = []
    warnings = []
    schema_tree = schema_package['schema_tree']
    root_name = schema_tree['name']

    if root_name not in nested_data:
        return {"dmaze_data": [], "warnings": [f"Input from AI is missing the root key '{root_name}'."]}

    # --- Step 1: Collect all entities to be matched ---
    print("\n--- Step 4a: Collecting all entities to be matched... ---")
    items_to_match = {}
    collect_entities_to_match(nested_data[root_name], schema_tree, items_to_match)
    
    # --- Step 2: Get valid entities and perform the batch match ---
    candidate_map = { entity_type: get_entities_from_api(entity_type) for entity_type in items_to_match.keys() }

    # Determine which types actually have candidates to match against
    matchable_types = {t for t, c in candidate_map.items() if c}
    skipped_types = set(items_to_match.keys()) - matchable_types
    for t in skipped_types:
        warning_msg = f"No predefined entities available for type '{t}'. Values for this type will be preserved as raw text and not matched to IDs."
        warnings.append(warning_msg)
        print(f"  - WARNING: {warning_msg}")

    print("\n--- Step 4b: Finding all ID matches in a single batch call... ---")
    # Only call the batch matcher for types that actually have candidate lists
    to_match = {t: items_to_match[t] for t in matchable_types}
    valid_entities_map = {t: candidate_map[t] for t in matchable_types}
    # Pass the ai_client instance to the batch matcher
    detailed_lookup_map = find_best_entity_matches_in_batch(ai_client, to_match, valid_entities_map)

    # --- STEP 3 Systematically check for "Not Found" errors BEFORE flattening ---
    print("\n--- Step 4c: Verifying all entities and collecting 'Not Found' warnings... ---")
    for entity_type, values_set in items_to_match.items():
        for value in values_set:
            # Check if a match was found for this specific value and type
            if not detailed_lookup_map.get(entity_type, {}).get(value):
                warning_msg = f"Match not found for '{value}' (Type: {entity_type}). The value was ignored."
                warnings.append(warning_msg)
                print(f"  - WARNING: {warning_msg}")

    # --- Step 4: Flatten the data using your original, working function ---
    # The `warnings` list is passed in, so `flatten_recursively` can add its low-confidence warnings to it.
    print("\n--- Step 4d: Transforming data structure... ---")
    flatten_recursively(
        ai_client=ai_client,
        data_node=nested_data[root_name],
        schema_node=schema_tree,
        parent_id=None,
        parent_type=None,
        flat_list=final_list,
        detailed_lookup_map=detailed_lookup_map,
        warnings=warnings
    )

    root_index = next((i for i, obj in enumerate(final_list) if obj.get('objectname') == root_name), -1)
    if root_index != -1:
        root_obj = final_list.pop(root_index)
        final_list.insert(0, root_obj)

    return {"dmaze_data": final_list, "warnings": warnings}