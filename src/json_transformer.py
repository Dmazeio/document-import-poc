# File: src/json_transformer.py
import uuid

# ENDRET: Funksjonen trenger nå 'entity_map' for å kunne oversette labels til ID-er.
def flatten_recursively(data_node: dict, schema_node: dict, parent_id: str, parent_type: str, flat_list: list, entity_map: dict):
    object_name = schema_node['name']
    
    node_id = f"{object_name}-{uuid.uuid4()}"
    dmaze_object = {
        "id": node_id,
        "objectname": object_name
    }
    if parent_id:
        dmaze_object["parentid"] = parent_id
        dmaze_object["parenttype"] = parent_type

    # ENDRET: Oppdatert logikk for å håndtere oversettelse av entities.
    for field_info in schema_node['fields']:
        field_name = field_info['fieldname']
        entity_key = field_info.get('entity')
        
        # Hent verdien fra AI-outputen.
        ai_value = data_node.get(field_name)

        # NYTT: Hvis det er en entity og vi har en verdi, slå opp ID-en.
        if entity_key and ai_value is not None:
            # Slå opp f.eks. entity_map["status"]["Draft"] -> "d-draft"
            # Hvis den ikke finner en match, bruker den bare rå-verdien fra AI-en som en fallback.
            final_value = entity_map.get(entity_key, {}).get(ai_value, ai_value) 
            dmaze_object[field_name] = final_value
        else:
            # Hvis ikke en entity, bruk verdien som den er.
            dmaze_object[field_name] = ai_value
    
    for child_schema in schema_node.get('children', []):
        child_name = child_schema['name']
        child_items = data_node.get(child_name, [])
        child_ids = []
        
        if child_items:
            for item in child_items:
                # ENDRET: Send 'entity_map' med i det rekursive kallet.
                child_id = flatten_recursively(item, child_schema, node_id, object_name, flat_list, entity_map)
                child_ids.append(child_id)
        
        relationship_field = child_schema['relationship_field']
        dmaze_object[relationship_field] = {
            "type": child_name,
            "values": child_ids
        }

    flat_list.append(dmaze_object)
    return node_id


# ENDRET: Funksjonen bør motta hele 'schema_package' for å få tilgang til alt den trenger.
def transform_to_dmaze_format_hierarchically(nested_data: dict, schema_package: dict) -> list:
    final_list = []
    
    # ENDRET: Hent ut alle nødvendige deler fra pakken.
    schema_tree = schema_package['schema_tree']
    entity_map = schema_package.get('entity_map', {}) # Hent mappingen
    
    root_name = schema_tree['name']

    if root_name not in nested_data:
        return [{"error": f"Input from AI is missing the root key '{root_name}' defined in the schema."}]

    # ENDRET: Send med 'entity_map' til den rekursive funksjonen.
    flatten_recursively(
        data_node=nested_data[root_name],
        schema_node=schema_tree,
        parent_id=None,
        parent_type=None,
        flat_list=final_list,
        entity_map=entity_map
    )

    # Re-ordering forblir uendret
    root_index = next((i for i, obj in enumerate(final_list) if obj.get('objectname') == root_name), -1)
    if root_index != -1:
        root_obj = final_list.pop(root_index)
        final_list.insert(0, root_obj)

    return final_list