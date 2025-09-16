# File: src/schema_processor.py (FINAL, 100% AUTONOMOUS VERSION)

import json

# Definer en global terskel. Hvis en liste med valg i malen er lengre enn dette,
# lager vi ikke en fast valgliste (enum) for AI-en.
ENUM_THRESHOLD = 25

#Denne funksjonen transformerer de flate listene med objekter og relasjoner om til én enkelt, hierarkisk trestruktur.
def build_schema_tree(object_name: str, types_map: dict, relationships: list, entities: dict) -> dict:
    """Recursively builds a hierarchical tree from the template's flat relationships."""
    object_info = types_map.get(object_name)
    if not object_info: return None

    node = { "name": object_name, "fields": object_info['fields'], "children": [] }
    
    for rel in relationships:
        if rel['parent'] == object_name:
            child_name = rel['child']
            child_node = build_schema_tree(child_name, types_map, relationships, entities)
            if child_node:
                child_node['relationship_field'] = rel['childfieldname']
                node['children'].append(child_node)
    return node

# Denne funksjonen oversetter den interne, forenklede trestrukturen (schema_tree) til et strengt og formelt JSON Schema.
def build_json_schema_from_tree(node: dict, entities: dict) -> dict:
    """Converts the internal schema tree into a formal JSON Schema for the OpenAI API."""
    properties = {}
    for field_info in node.get('fields', []):
        field_name = field_info['fieldname']
        field_type = field_info.get('type')
        entity_key = field_info.get('entitytype')

        # --- START PÅ DEN NYE, AUTONOME LOGIKKEN ---
        # Lag en fast valgliste (enum) KUN HVIS:
        # 1. Det er en entitetstype som finnes i 'entities'-blokken i malen.
        # 2. Antallet valgmuligheter for den entiteten er UNDER vår definerte terskel.
        if entity_key and entity_key in entities and len(entities[entity_key]) <= ENUM_THRESHOLD:
            print(f"    - Creating enum for '{entity_key}' (found {len(entities[entity_key])} items, threshold is {ENUM_THRESHOLD}).")
            valid_names = [item['name'] for item in entities[entity_key]]
            properties[field_name] = {
                "type": ["string", "null"],
                "description": f"Must be one of: {', '.join(valid_names)}. If not mentioned, use null.",
                "enum": valid_names + [None]
            }
       
        elif field_type in ['datetime', 'date']:
            properties[field_name] = {"type": ["string", "null"], "format": "date-time"}
        else:
            # For alle andre felter (inkludert 'user' som ikke er i 'entities', eller lister som er for lange), be om ren tekst.
            if entity_key:
                 print(f"    - Skipping enum for '{entity_key}' (list not found in template or too long). Treating as free text.")
            properties[field_name] = {
                "type": ["string", "null"],
                "description": f"The {field_name}. Extract the value as plain text. For entities like people, extract their full name or names."
            }

    for child in node.get('children', []):
        properties[child['name']] = { "type": "array", "items": build_json_schema_from_tree(child, entities) }
    
    required_fields = [field['fieldname'] for field in node.get('fields', [])] + [child['name'] for child in node.get('children', [])]

    return { "type": "object", "properties": properties, "required": required_fields, "additionalProperties": False }

#Denne hovedfunksjonen orkestrerer lesingen av en JSON-mal...
def process_template_hierarchically(template_path: str) -> dict:
    """
    Main function to read ANY template file and generate the necessary schema artifacts.
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)

        types_data = template.get('types', [])
        types_map = {}
    
        if isinstance(types_data, dict):
            print("  - Schema format detected: 'types' is a dictionary.")
            types_map = {t['objectname']: t for t in types_data.values()}
        elif isinstance(types_data, list):
            print("  - Schema format detected: 'types' is a list.")
            types_map = {t['objectname']: t for t in types_data}
        else:
            return {"error": "'types' key in template is neither a list nor a dictionary."}

        print("  - Discovering relationships...")
        unified_relationships = template.get('relationships', [])
        
        for object_name, object_info in types_map.items():
            for field in object_info.get('fields', []):
                field_entity_type = field.get('entitytype')
                if field_entity_type and field_entity_type in types_map:
                    print(f"    - Found implicit relationship: {object_name} -> {field_entity_type}")
                    new_rel = {"parent": object_name, "child": field_entity_type, "childfieldname": field['fieldname']}
                    if not any(r['parent'] == new_rel['parent'] and r['child'] == new_rel['child'] for r in unified_relationships):
                        unified_relationships.append(new_rel)

        entities = template.get('entities', {})

        root_object_info = next((t for t in types_map.values() if t.get('isroot')), None)
        if not root_object_info:
            return {"error": "Could not find a root object with 'isroot: true' in the template."}

        root_name = root_object_info['objectname']
        
        print("  - Building schema for AI...")
        schema_tree = build_schema_tree(root_name, types_map, unified_relationships, entities)
        formal_json_schema = build_json_schema_from_tree(schema_tree, entities)
        
        final_schema_for_api = {
            "type": "object",
            "properties": {root_name: formal_json_schema},
            "required": [root_name],
            "additionalProperties": False
        }
        
        entity_map = { entity_key: {item['name']: item['id'] for item in items} for entity_key, items in entities.items()}

        return {"schema_tree": schema_tree, "json_schema_for_api": final_schema_for_api, "entity_map": entity_map}
    except Exception as e:
         return {"error": f"Template file has a malformed key/structure: {e}"}