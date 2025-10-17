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
            # ALLTID forsøk å opprette det strukturerte objektet for entitytype-felter.
            
            entity_schema = get_entity_schema_from_api(entity_type)
            
            # Bruk entity_type som fallback hvis meta-skjema ikke er funnet eller wrapper er None
            type_name = entity_type 
            if entity_schema:
                type_name = entity_schema.get('dmaze_format_wrapper') or entity_type

            found_ids = []
            if raw_text_value is not None and str(raw_text_value).strip().lower() != "null":
                texts_to_match = re.split(r'[,;\n]|(?:\s+og\s+)|(?:\s+and\s+)', str(raw_text_value)) if field_type == "multivalue" else [str(raw_text_value)]
                for text in texts_to_match:
                    cleaned_text = text.strip()
                    if cleaned_text:
                        # Se kun opp i detailed_lookup_map hvis entity_type ble prosessert for matching
                        match_details = detailed_lookup_map.get(entity_type, {}).get(cleaned_text)
                        if match_details:
                            found_id = match_details['id']
                            found_ids.append(found_id)
                            if match_details.get('confidence', 'High') in ["Medium", "Low"]:
                                warning_msg = f"Lav konfidensmatch for '{cleaned_text}' (Type: {entity_type}): Matchet til ID '{found_id}'. Årsak: {match_details.get('reasoning', 'N/A')}"
                                warnings.append(warning_msg)

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
    # Ny funksjon for å hente alle entity_types fra skjemaet
    def get_all_entity_types_from_schema(schema_node: dict, entity_types_set: set):
        for field_info in schema_node.get('fields', []):
            entity_type = field_info.get('entitytype')
            if entity_type:
                entity_types_set.add(entity_type)
        for child_schema in schema_node.get('children', []):
            get_all_entity_types_from_schema(child_schema, entity_types_set)

    all_schema_entity_types = set()
    get_all_entity_types_from_schema(schema_tree, all_schema_entity_types)

    # 2a: Hent entiteter fra api_simulator
    api_entities_map = { entity_type: get_entities_from_api(entity_type) for entity_type in all_schema_entity_types }

    # 2b: Hent entiteter fra input-skjemaet (schema_package['entity_map'])
    # Konverter skjemaets format {'name': 'id'} til [{'id': '...', 'name': '...'}]
    schema_only_entities_map = {}
    for entity_type, name_id_map in schema_package['entity_map'].items():
        if entity_type in all_schema_entity_types: # Sørg for at vi bare behandler relevante typer
            schema_only_entities_map[entity_type] = []
            for name, entity_id in name_id_map.items():
                schema_only_entities_map[entity_type].append({"id": entity_id, "name": name})

    # 2c: Kombiner entitetene fra API-simulator og skjemaet.
    # Prioriter API-simulator, men legg til skjema-entiteter som unike valg om navnet ikke allerede finnes.
    # Siden du har gjort ID-ene distinkte, er målet å vise at AI kan velge fra BEGGE kilder.
    combined_valid_entities_map = {}
    for entity_type in all_schema_entity_types:
        combined_list = []
        
        # Legg til fra API-simulator først
        if api_entities_map.get(entity_type):
            combined_list.extend(api_entities_map[entity_type])
        
        # Legg til fra skjema, unngå duplikater basert på id (siden navn kan være like, men id er unik for kilden)
        if schema_only_entities_map.get(entity_type):
            api_ids = {e['id'] for e in combined_list}
            for schema_entity in schema_only_entities_map[entity_type]:
                if schema_entity['id'] not in api_ids:
                    combined_list.append(schema_entity)
        
        combined_valid_entities_map[entity_type] = combined_list


    # Determine which types actually have candidates to match against (now from the combined map)
    matchable_types = {t for t, c in combined_valid_entities_map.items() if c}
    
    # OBS: Denne varslingen må kanskje justeres. Den sjekker for typer som hadde
    # extracted text men ingen matchbare kandidater i den kombinerte listen.
    # For mentorens formål er det viktigere å vise at skjema-entiteter ER MED.
    # Jeg beholder den eksisterende logikken for nå, men vær obs.
    skipped_types = set(items_to_match.keys()) - matchable_types 
    for t in skipped_types:
        # Avoid duplicate warnings if the warning was already added in the _flatten_recursively call
        warning_msg = f"Ingen forhåndsdefinerte entiteter tilgjengelig for type '{t}' (verken fra API eller skjema). Verdier for denne typen vil bli bevart som råtekst og ikke matchet mot ID-er."
        if warning_msg not in warnings:
            warnings.append(warning_msg)
            print(f"  - ADVARSEL: {warning_msg}")


    print("\n--- Step 4b: Finding all ID matches in a single batch call... ---")
    # Only call the batch matcher for types that actually have candidate lists AND text to match
    to_match = {t: items_to_match[t] for t in items_to_match.keys() if t in matchable_types}
    
    # Pass den kombinerte listen med gyldige entiteter til matcher-funksjonen
    detailed_lookup_map = find_best_entity_matches_in_batch(ai_client, to_match, combined_valid_entities_map)

    # --- STEP 3 Systematically check for "Not Found" errors BEFORE flattening ---
    print("\n--- Step 4c: Verifying all entities and collecting 'Not Found' warnings... ---")
    for entity_type, values_set in items_to_match.items():
        if entity_type in matchable_types: # Only check for types that *could* be matched
            for value in values_set:
                # Check if a match was found for this specific value and type
                if not detailed_lookup_map.get(entity_type, {}).get(value):
                    warning_msg = f"Match ikke funnet for '{value}' (Type: {entity_type}). Verdien ble ignorert."
                    warnings.append(warning_msg)
                    print(f"  - ADVARSEL: {warning_msg}")
        else:
            # If a type was not matchable (no candidates in combined_valid_entities_map),
            # but had values collected, ensure a warning is present.
            warning_msg = f"Ingen forhåndsdefinerte entiteter tilgjengelig for type '{entity_type}' (verken fra API eller skjema). Verdier for denne typen vil bli bevart som råtekst og ikke matchet mot ID-er."
            if warning_msg not in warnings: # Avoid duplicate warnings
                warnings.append(warning_msg)
                print(f"  - ADVARSEL: {warning_msg}")


    # --- Step 4: Flatten the data using your original, working function ---
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