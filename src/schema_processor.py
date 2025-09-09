# File: src/schema_processor.py (FINAL, CORRECT HYBRID VERSION)

import json

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

def build_json_schema_from_tree(node: dict, entities: dict) -> dict:
    """Converts the internal schema tree into a formal JSON Schema for the OpenAI API."""
    properties = {}
    for field_info in node.get('fields', []):
        field_name = field_info['fieldname']
        field_type = field_info.get('type')
        entity_key = field_info.get('entitytype')

        # HYBRID LOGIC:
        # For most entities, build an enum to guide the AI. For 'user', ask for plain text.
        if entity_key and entity_key in entities and entity_key != 'user':
            valid_names = [item['name'] for item in entities[entity_key]]
            properties[field_name] = {
                "type": ["string", "null"],
                "description": f"Must be one of: {', '.join(valid_names)}. If not mentioned, use null.",
                "enum": valid_names + [None]
            }
        elif field_type == 'datetime':
            properties[field_name] = {"type": ["string", "null"], "format": "date-time"}
        else:
            # Applies to 'user' fields and regular string fields.
            properties[field_name] = {
                "type": ["string", "null"],
                "description": f"The {field_name}. Extract the value as plain text from the document. For people, extract their full name."
            }

    for child in node.get('children', []):
        properties[child['name']] = { "type": "array", "items": build_json_schema_from_tree(child, entities) }
    
    required_fields = [field['fieldname'] for field in node.get('fields', [])] + [child['name'] for child in node.get('children', [])]

    return { "type": "object", "properties": properties, "required": required_fields, "additionalProperties": False }

def process_template_hierarchically(template_path: str) -> dict:
    """
    Main function to read a template file and generate the schema tree, the JSON schema for the API, and an entity map.
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)

        types_map = {t['objectname']: t for t in template.get('types', [])}
        relationships = template.get('relationships', [])
        entities = template.get('entities', {})

        root_object_info = next((t for t in template['types'] if t.get('isroot')), None)
        if not root_object_info: return {"error": "Could not find a root object in the template."}

        root_name = root_object_info['objectname']
        
        # 1. Build the internal hierarchical tree representation.
        schema_tree = build_schema_tree(root_name, types_map, relationships, entities)

        # 2. Convert the tree into a formal JSON Schema for the API call.
        formal_json_schema = build_json_schema_from_tree(schema_tree, entities)
        final_schema_for_api = {
            "type": "object",
            "properties": { root_name: formal_json_schema },
            "required": [root_name],
            "additionalProperties": False
        }
        
        # 3. Create a map for quick name-to-ID lookups for entities.
        entity_map = {
            entity_key: {item['name']: item['id'] for item in items}
            for entity_key, items in entities.items()
        }

        # Return a package with all the generated artifacts.
        return { "schema_tree": schema_tree, "json_schema_for_api": final_schema_for_api, "entity_map": entity_map }
    except Exception as e:
         return {"error": f"Template file has a malformed key/structure: {e}"}