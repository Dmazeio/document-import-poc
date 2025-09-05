# File: src/schema_processor.py
import json

def build_schema_tree(object_name: str, types_map: dict, relationships: list) -> dict:
    # This function is correct and unchanged
    object_info = types_map.get(object_name)
    if not object_info:
        return None
    node = {
        "name": object_name,
        "fields": [field['fieldname'] for field in object_info['fields']],
        "children": []
    }
    for rel in relationships:
        if rel['parent'] == object_name:
            child_name = rel['child']
            child_node = build_schema_tree(child_name, types_map, relationships)
            if child_node:
                child_node['relationship_field'] = rel['childfieldname']
                node['children'].append(child_node)
    return node

def build_json_schema_from_tree(node: dict) -> dict:
    # The change is in this function
    properties = {}
    for field in node.get('fields', []):
        if "time" in field.lower() or "date" in field.lower():
            properties[field] = {"type": "string", "format": "date-time", "description": f"The {field} of the object."}
        else:
            properties[field] = {"type": "string", "description": f"The {field} of the object."}

    for child in node.get('children', []):
        properties[child['name']] = {
            "type": "array",
            "items": build_json_schema_from_tree(child)
        }

    # CHANGE IS HERE: The 'required' array must list all keys defined in 'properties'.
    # This includes both the simple data fields AND the nested child arrays.
    required_fields = node.get('fields', []) + [child['name'] for child in node.get('children', [])]

    return {
        "type": "object",
        "properties": properties,
        "required": required_fields,
        "additionalProperties": False
    }


def process_template_hierarchically(template_path: str) -> dict:
    # This function is correct and unchanged
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)

        types_map = {t['objectname']: t for t in template.get('types', [])}
        relationships = template.get('relationships', [])
        # entities = template.get('entities', [])
        root_object_info = next((t for t in template['types'] if t.get('isroot')), None)
        if not root_object_info:
            return {"error": "Could not find a root object (isroot: true) in the template."}

        root_name = root_object_info['objectname']
        schema_tree = build_schema_tree(root_name, types_map, relationships)

        if not schema_tree:
             return {"error": "Failed to build the schema tree."}

        formal_json_schema = build_json_schema_from_tree(schema_tree)
        
        final_schema_for_api = {
            "type": "object",
            "properties": {
                root_name: formal_json_schema
            },
            "required": [root_name],
            "additionalProperties": False
        }

        return {
            "schema_tree": schema_tree,
            "json_schema_for_api": final_schema_for_api
        }

    except FileNotFoundError:
        return {"error": f"Template file not found at: {template_path}"}
    except (json.JSONDecodeError, KeyError, IndexError, StopIteration) as e:
         return {"error": f"The template file has a missing or malformed key/structure: {e}"}