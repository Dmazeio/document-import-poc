# File: src/schema_processor.py

import json

def process_template(template_path: str) -> dict:
    """
    Reads a Dmaze JSON template and extracts a simple "recipe" (metadata)
    that the rest of the system can use dynamically.
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)

        # Find the root object (the parent) based on "isroot": true
        root_object_info = next((t for t in template['types'] if t.get('isroot')), None)
        if not root_object_info:
            return {"error": "Could not find a root object (isroot: true) in the template."}

        # Find the relationship information
        relationship_info = template['relationships'][0] if template.get('relationships') else None
        if not relationship_info:
            return {"error": "Could not find relationship info in the template."}
            
        # Find the child object based on the name in the relationship
        child_object_name = relationship_info['child']
        child_object_info = next((t for t in template['types'] if t.get('objectname') == child_object_name), None)
        if not child_object_info:
            return {"error": f"Could not find the child object '{child_object_name}' defined in relationships."}

        # Create the simple "recipe" that the other functions need
        schema_metadata = {
            "parent_name": root_object_info['objectname'],
            "parent_fields": [field['fieldname'] for field in root_object_info['fields']],
            "child_name": child_object_info['objectname'],
            "child_fields": [field['fieldname'] for field in child_object_info['fields']],
            "relationship_field": relationship_info['childfieldname']
        }
        return schema_metadata

    except FileNotFoundError:
        return {"error": f"Template file not found at: {template_path}"}
    except json.JSONDecodeError:
        return {"error": f"Could not parse the JSON in the template file: {template_path}"}
    except (KeyError, IndexError) as e:
         return {"error": f"The template file has a missing or malformed key/structure: {e}"}