# File: src/schema_processor.py (UNIVERSAL VERSION)

import json

#Denne funksjonen transformerer de flate listene med objekter og relasjoner om til én enkelt, hierarkisk trestruktur.
def build_schema_tree(object_name: str, types_map: dict, relationships: list, entities: dict) -> dict:
    """Recursively builds a hierarchical tree from the template's flat relationships."""
    object_info = types_map.get(object_name)
    if not object_info: return None

    node = { "name": object_name, "fields": object_info['fields'], "children": [] }
    
    # Denne løkken fungerer perfekt så lenge 'relationships' er en komplett liste.
    for rel in relationships:
        if rel['parent'] == object_name:
            child_name = rel['child']
            child_node = build_schema_tree(child_name, types_map, relationships, entities)
            if child_node:
                child_node['relationship_field'] = rel['childfieldname']
                node['children'].append(child_node)
    return node


# Denne funksjonen oversetter den interne, forenklede trestrukturen (schema_tree) til et strengt og formelt JSON Schema, som fungerer som en detaljert teknisk instruks for AI-modellen 
def build_json_schema_from_tree(node: dict, entities: dict) -> dict:
    """Converts the internal schema tree into a formal JSON Schema for the OpenAI API."""
    properties = {}
    for field_info in node.get('fields', []):
        field_name = field_info['fieldname']
        field_type = field_info.get('type')
        entity_key = field_info.get('entitytype')

        # Denne logikken fungerer fortsatt bra for å guide AI-en.
        if entity_key and entity_key in entities and entity_key not in ['user', 'people']: # Unngår å lage enum for brukere
            valid_names = [item['name'] for item in entities[entity_key]]
            properties[field_name] = {
                "type": ["string", "null"],
                "description": f"Must be one of: {', '.join(valid_names)}. If not mentioned, use null.",
                "enum": valid_names + [None]
            }
        elif field_type in ['datetime', 'date']:
            properties[field_name] = {"type": ["string", "null"], "format": "date-time"}
        else:
            properties[field_name] = {
                "type": ["string", "null"],
                "description": f"The {field_name}. Extract the value as plain text. For people, extract their full name or names."
            }
        #Gjøre slik at vi ikke ser på field_name man at vi heller ser på desciription
        

    for child in node.get('children', []):
        properties[child['name']] = { "type": "array", "items": build_json_schema_from_tree(child, entities) }
    
    required_fields = [field['fieldname'] for field in node.get('fields', [])] + [child['name'] for child in node.get('children', [])]

    return { "type": "object", "properties": properties, "required": required_fields, "additionalProperties": False }

#Denne hovedfunksjonen orkestrerer lesingen av en JSON-mal, bygger en intern hierarkisk trestruktur (schema_tree), og genererer deretter et formelt JSON Schema som brukes til å instruere AI-modellen nøyaktig hvordan den skal formatere sitt svar.
def process_template_hierarchically(template_path: str) -> dict:
    """
    Main function to read ANY template file and generate the necessary schema artifacts.
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)

        # === ENDRING 1: Fleksibel "types"-håndtering ===
        types_data = template.get('types', [])
        types_map = {}
    
        if isinstance(types_data, dict):
            # Håndterer det nye formatet der 'types' er et objekt/ordbok
            print("  - Schema format detected: 'types' is a dictionary.")
            types_map = {t['objectname']: t for t in types_data.values()}
        elif isinstance(types_data, list):
            # Håndterer det gamle formatet der 'types' er en liste
            print("  - Schema format detected: 'types' is a list.")
            types_map = {t['objectname']: t for t in types_data}
        else:
            return {"error": "'types' key in template is neither a list nor a dictionary."}

        # === ENDRING 2: Relasjonsdetektiven - Finn ALLE relasjoner ===
        print("  - Discovering relationships...")
        # Start med de eksplisitte relasjonene
        unified_relationships = template.get('relationships', [])
        
        # Finn implisitte relasjoner definert i feltene
        for object_name, object_info in types_map.items():
            for field in object_info.get('fields', []):
                field_entity_type = field.get('entitytype')
                # En implisitt relasjon eksisterer hvis et felts 'entitytype'
                # matcher navnet på et annet kjent objekt (f.eks. 'agenda').
                if field_entity_type and field_entity_type in types_map:
                    print(f"    - Found implicit relationship: {object_name} -> {field_entity_type}")
                    new_rel = {
                        "parent": object_name,
                        "child": field_entity_type,
                        "childfieldname": field['fieldname']
                    }
                    # Unngå duplikater hvis relasjonen allerede er definert
                    if not any(r['parent'] == new_rel['parent'] and r['child'] == new_rel['child'] for r in unified_relationships):
                        unified_relationships.append(new_rel)

        # Resten av logikken bruker nå den komplette, forente listen med relasjoner
        entities = template.get('entities', {})

        root_object_info = next((t for t in types_map.values() if t.get('isroot')), None)
        if not root_object_info:
            return {"error": "Could not find a root object with 'isroot: true' in the template."}

        root_name = root_object_info['objectname']
        
        # 1. Bygg treet ved hjelp av den nye, komplette relasjonslisten
        schema_tree = build_schema_tree(root_name, types_map, unified_relationships, entities) #  Lengre opp i filen (2) 

        # 2. Konverter treet til en formell JSON Schema for AI-kallet (som før)
        formal_json_schema = build_json_schema_from_tree(schema_tree, entities)  #   Lengre opp i filen (3) 
        final_schema_for_api = {
            "type": "object",
            "properties": {root_name: formal_json_schema},
            "required": [root_name],
            "additionalProperties": False
        }
        
        # 3. Lag oppslagstabell for statiske entiteter (som før)
        entity_map = {
            entity_key: {item['name']: item['id'] for item in items}
            for entity_key, items in entities.items()
        }

        # Returner den komplette pakken
        return {
            "schema_tree": schema_tree,
            "json_schema_for_api": final_schema_for_api,
            "entity_map": entity_map
        }
    except Exception as e:
         return {"error": f"Template file has a malformed key/structure: {e}"}
    
    #  tilabake til main.py (4)