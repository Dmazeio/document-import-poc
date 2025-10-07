# File: src/schema_processor.py (MODIFIED TO PRIORITIZE FIELD DESCRIPTIONS)

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
    """
    Converts the internal schema tree into a formal JSON Schema for the OpenAI API.
    This version PRIORITIZES the rich 'description' from the template as the main instruction for the AI.
    """
    properties = {}
    for field_info in node.get('fields', []):
        field_name = field_info['fieldname']
        field_type = field_info.get('type')
        entity_key = field_info.get('entitytype')

        # === KJERNEENDRINGEN: Bruk den rike beskrivelsen fra malen som hovedinstruks ===
        # Dette gir AI-en best mulig kontekst for HVA den skal lete etter.
        ai_instruction = field_info.get('description', f"Extract data for the field named '{field_name}'.")

        # Start med en basis-definisjon for feltet i JSON Schemaet
        schema_field = {
            "type": ["string", "null"],
            "description": ai_instruction  # Her settes den rike beskrivelsen!
        }

        # Legg til spesifikke, tekniske krav PÅ TOPPEN av den rike beskrivelsen.
        # Dette gir AI-en både kontekst (hva) og format (hvordan).
        
        # For felt som peker til en liste med forhåndsdefinerte valg (entities)
        if entity_key and entity_key in entities and entity_key not in ['user', 'people']:
            valid_names = [item['name'] for item in entities[entity_key]]
            # Legg til en presis instruksjon om de gyldige valgene
            schema_field['description'] += f"\n\nIMPORTANT: The value MUST be one of the following, or null: {', '.join(valid_names)}."
            schema_field['enum'] = valid_names + [None]
        
        # For dato- og tidsfelter
        elif field_type in ['datetime', 'date']:
            schema_field['format'] = "date-time"
            schema_field['description'] += "\n\nIMPORTANT: Format the value as a valid ISO 8601 date-time string (e.g., YYYY-MM-DDTHH:MM:SSZ)."

        # For alle andre felter (vanlig tekst), er standarddefinisjonen allerede perfekt.
        
        properties[field_name] = schema_field

    for child in node.get('children', []):
        properties[child['name']] = { "type": "array", "items": build_json_schema_from_tree(child, entities) }
    
    required_fields = [field['fieldname'] for field in node.get('fields', [])] + [child['name'] for child in node.get('children', [])]

    return { "type": "object", "properties": properties, "required": required_fields, "additionalProperties": False }


#Denne hovedfunksjonen orkestrerer lesingen av en JSON-mal, bygger en intern hierarkisk trestruktur (schema_tree), og genererer deretter et formelt JSON Schema som brukes til å instruere AI-modellen nøyaktig hvordan den skal formatere sitt svar.
def process_template_hierarchically(schema_content: dict):
    """
    Main function to read ANY template file and generate the necessary schema artifacts.
    """
    try:

        # === ENDRING 1: Fleksibel "types"-håndtering ===
        types_data = schema_content.get('types', [])
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
        unified_relationships = schema_content.get('relationships', [])
        
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
        entities = schema_content.get('entities', {})

        root_object_info = next((t for t in types_map.values() if t.get('isroot')), None)
        if not root_object_info:
            return {"error": "Could not find a root object with 'isroot: true' in the template."}

        root_name = root_object_info['objectname']
        
        # 1. Bygg treet ved hjelp av den nye, komplette relasjonslisten
        schema_tree = build_schema_tree(root_name, types_map, unified_relationships, entities) 

        # 2. Konverter treet til en formell JSON Schema for AI-kallet (som før)
        formal_json_schema = build_json_schema_from_tree(schema_tree, entities)  
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