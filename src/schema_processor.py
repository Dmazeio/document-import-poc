import json

# Convert flat lists of types and relationships into a hierarchical tree structure.
def build_schema_tree(object_name: str, types_map: dict, relationships: list, entities: dict) -> dict:
    """Recursively builds a hierarchical tree from the template's flat relationships."""
    object_info = types_map.get(object_name)
    if not object_info: return None

    node = {"name": object_name, "fields": object_info.get('fields', []), "children": []}

    # Attach children based on explicit relationships
    for rel in relationships:
        if rel['parent'] == object_name:
            child_name = rel['child']
            child_node = build_schema_tree(child_name, types_map, relationships, entities)
            if child_node:
                child_node['relationship_field'] = rel['childfieldname']
                node['children'].append(child_node)
    return node


def build_json_schema_from_tree(node: dict, entities: dict) -> dict:
    """
    Converts the internal schema tree into a formal JSON Schema suitable for instructing an AI model.
    Field descriptions from the template are used as the primary instruction for extraction.
    """
    properties = {}

    for field_info in node.get('fields', []):
        field_name = field_info.get('fieldname')
        field_type = field_info.get('type')
        entity_key = field_info.get('entitytype')

        # Use template description as the main instruction for the AI
        ai_instruction = field_info.get('description', f"Extract data for the field named '{field_name}'.")

        schema_field = {
            "type": ["string", "null"],
            "description": ai_instruction 
        }

        # For fields that reference a predefined entity list, add enum when safe
        if entity_key and entity_key in entities and entity_key not in ['user', 'people']:
            valid_names = [item['name'] for item in entities[entity_key]]
            schema_field['description'] += f"\n\nIMPORTANT: The value MUST be one of the following, or null: {', '.join(valid_names)}."
            schema_field['enum'] = valid_names + [None]
        
        elif field_type in ['datetime', 'date']:
            schema_field['format'] = "date-time"
            schema_field['description'] += "\n\nIMPORTANT: Format the value as a valid ISO 8601 date-time string (e.g., YYYY-MM-DDTHH:MM:SSZ)."

        properties[field_name] = schema_field

    # Recursively add children as arrays of objects
    for child in node.get('children', []):
        properties[child['name']] = { "type": "array", "items": build_json_schema_from_tree(child, entities) }
    
    required_fields = [field['fieldname'] for field in node.get('fields', [])] + [child['name'] for child in node.get('children', [])]

    return {"type": "object", "properties": properties, "required": required_fields, "additionalProperties": False}


def process_template_hierarchically(schema_content: dict):
    """
    Main function to read any template file and generate the artifacts needed by the pipeline:
      - schema_tree: a hierarchical representation used for traversal/flattening
      - json_schema_for_api: a formal JSON Schema sent to the AI
      - entity_map: a name->id lookup for static entities defined in the template
    """
    try:
        types_data = schema_content.get('types', [])
        types_map = {}

        if isinstance(types_data, dict):
            # Newer format where 'types' is an object mapping
            print("  - Schema format detected: 'types' is a dictionary.")
            types_map = {t['objectname']: t for t in types_data.values()}
        elif isinstance(types_data, list):
            # Legacy format where 'types' is a list
            print("  - Schema format detected: 'types' is a list.")
            types_map = {t['objectname']: t for t in types_data}
        else:
            return {"error": "'types' key in template is neither a list nor a dictionary."}

        # Discover relationships: start with explicit ones and add implicit ones based on field entitytypes
        print("  - Discovering relationships...")
        unified_relationships = schema_content.get('relationships', [])

        for object_name, object_info in types_map.items():
            for field in object_info.get('fields', []):
                field_entity_type = field.get('entitytype')
                if field_entity_type and field_entity_type in types_map:
                    print(f"    - Found implicit relationship: {object_name} -> {field_entity_type}")
                    new_rel = {
                        "parent": object_name,
                        "child": field_entity_type,
                        "childfieldname": field.get('fieldname')
                    }
                    if not any(r['parent'] == new_rel['parent'] and r['child'] == new_rel['child'] for r in unified_relationships):
                        unified_relationships.append(new_rel)

        entities = schema_content.get('entities', {})

        root_object_info = next((t for t in types_map.values() if t.get('isroot')), None)
        if not root_object_info:
            return {"error": "Could not find a root object with 'isroot: true' in the template."}

        root_name = root_object_info['objectname']

        # Build tree and the formal JSON schema
        schema_tree = build_schema_tree(root_name, types_map, unified_relationships, entities)
        formal_json_schema = build_json_schema_from_tree(schema_tree, entities)
        final_schema_for_api = {
            "type": "object",
            "properties": {root_name: formal_json_schema},
            "required": [root_name],
            "additionalProperties": False
        }
        
        # Build entity map for name->id lookups
        entity_map = {
            entity_key: {item['name']: item['id'] for item in items}
            for entity_key, items in entities.items()
        }

        return {
            "schema_tree": schema_tree,
            "json_schema_for_api": final_schema_for_api,
            "entity_map": entity_map
        }

    except Exception as e:
        return {"error": f"Template file has a malformed key/structure: {e}"}