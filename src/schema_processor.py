# File: src/schema_processor.py
import json

def build_schema_tree(object_name, types_map, relationships):
    """
    A recursive function to build a hierarchical schema tree.
    """
    # Get the definition for the current object
    object_info = types_map.get(object_name)
    if not object_info:
        return None

    # This is the node for our current object
    node = {
        "name": object_name,
        "fields": [field['fieldname'] for field in object_info['fields']],
        "children": []
    }

    # Find all relationships where this object is the parent
    for rel in relationships:
        if rel['parent'] == object_name:
            child_name = rel['child']
            # Recursively build the tree for the child
            child_node = build_schema_tree(child_name, types_map, relationships)
            if child_node:
                # Add relationship info needed for transformation later
                child_node['relationship_field'] = rel['childfieldname']
                node['children'].append(child_node)

    return node

def process_template_hierarchically(template_path: str) -> dict:
    """
    Reads a Dmaze JSON template and builds a full hierarchical "recipe" (a schema tree)
    that the rest of the system can use.
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)

        # Create a map for quick lookup of object types by name
        types_map = {t['objectname']: t for t in template.get('types', [])}
        relationships = template.get('relationships', [])

        # Find the root object (the top of the tree)
        root_object_info = next((t for t in template['types'] if t.get('isroot')), None)
        if not root_object_info:
            return {"error": "Could not find a root object (isroot: true) in the template."}

        # Start building the tree from the root
        root_name = root_object_info['objectname']
        schema_tree = build_schema_tree(root_name, types_map, relationships)

        if not schema_tree:
             return {"error": "Failed to build the schema tree."}

        return schema_tree

    except FileNotFoundError:
        return {"error": f"Template file not found at: {template_path}"}
    except json.JSONDecodeError:
        return {"error": f"Could not parse the JSON in the template file: {template_path}"}
    except (KeyError, IndexError, StopIteration) as e:
         return {"error": f"The template file has a missing or malformed key/structure: {e}"}