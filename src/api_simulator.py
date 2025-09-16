# File: src/api_simulator.py (FINAL, CLEANED UP VERSION)

# Denne ordboken simulerer hele Dmaze-databasen med data.
SIMULATED_DATABASE = {
    # --- DATA FROM 'Minutes of Meeting' ---
    "user": [
        {"id": "user-1-ola-nordmann-uuid", "name": "Ola Nordmann", "email": "ola@example.com"},
        {"id": "user-2-kari-normann-uuid", "name": "Kari Nordmann", "email": "kari@example.com"},
        {"id": "user-3-arne-arnesen-uuid", "name": "Arne Arnesen", "email": "arne@example.com"},
        {"id": "user-4-lise-nilsen-uuid", "name": "Lise Nilsen", "email": "lise@example.com"},
        {"id": "user-5-arne-pettersen-uuid", "name": "Arne Pettersen", "email": "arne.p@example.com"},
        {"id": "user-6-ola-hansen-uuid", "name": "Ola Hansen", "email": "ola.hansen@example.com"},
    ],
    "people": [ # 'people' er et alias for 'user' og har samme data
        {"id": "user-1-ola-nordmann-uuid", "name": "Ola Nordmann"}, {"id": "user-2-kari-normann-uuid", "name": "Kari Nordmann"},
        {"id": "user-3-arne-arnesen-uuid", "name": "Arne Arnesen"}, {"id": "user-4-lise-nilsen-uuid", "name": "Lise Nilsen"},
        {"id": "user-5-arne-pettersen-uuid", "name": "Arne Pettersen"}, {"id": "user-6-ola-hansen-uuid", "name": "Ola Hansen"},
    ],
    "project": [
        {"id": "2", "name": "Admin"}, {"id": "3", "name": "Communication"}, {"id": "4", "name": "External/Partner"},
        {"id": "6", "name": "HR"}, {"id": "7", "name": "IT"}, {"id": "8", "name": "Management"},
        {"id": "9", "name": "Production"}, {"id": "5", "name": "R&D"}, {"id": "10", "name": "Sale"},
    ],
    "momstatus": [{"id": "3", "name": "Closed"}, {"id": "1", "name": "Draft"}, {"id": "2", "name": "Open"}],
    "typeofmeeting": [{"id": "1", "name": "Management meeting"}, {"id": "2", "name": "Status meeting"}],
    "unit": [{"id": "unit-1", "name": "Finance Department"}, {"id": "unit-2", "name": "Operations Division"}],
    "measurestate": [{"id": "1", "name": "Identified (pending decision)"}, {"id": "4", "name": "In progress (not started)"}, {"id": "12", "name": "Completed (100%) (approved)"}],
    "location": [{"id": "loc-1-oslo-uuid", "name": "Møterom Oslo"}, {"id": "loc-2-bergen-uuid", "name": "Prosjektrom Bergen"}],
    "meetingfrequency": [{"id": "2", "name": "One-off"}, {"id": "1", "name": "Recurring"}],
    "agendastatus": [{"id": "3", "name": "Closed"}, {"id": "1", "name": "Draft"}, {"id": "2", "name": "Open"}],
    "measurepriority": [{"id": "1", "name": "High"}, {"id": "3", "name": "Low"}, {"id": "2", "name": "Medium"}],

    # --- DATA FROM 'Emergency Preparedness' ---
    "epphase": [{"id": "3", "name": "Normalisation"}, {"id": "1", "name": "Notification and mobilisation"}, {"id": "2", "name": "Handling"}],
    "epplanrole": [{"id": "3", "name": "Fire response leader"}, {"id": "1", "name": "Emergency manager"}],
    "epresourcecategory": [{"id": "1", "name": "Cooperative partner"}, {"id": "2", "name": "Competence"}, {"id": "3", "name": "Manning"}, {"id": "4", "name": "Equipment"}],
    "epresourcestatus": [{"id": "5", "name": "Not relevant"}, {"id": "1", "name": "Identified"}, {"id": "2", "name": "Part of today's preparedness"}],
    "epassessmentstatus": [{"id": "3", "name": "Closed"}, {"id": "1", "name": "Draft"}, {"id": "2", "name": "Open"}],
    "epscenariostatus": [{"id": "1", "name": "Identified"}, {"id": "3", "name": "Not analysed"}, {"id": "2", "name": "Analysed"}],
    "eptaskstatus": [{"id": "1", "name": "Identified"}, {"id": "2", "name": "Part of today's preparedness"}],
    "epscenariocategory": [{"id": "1", "name": "Natural event"}, {"id": "2", "name": "Fire event"}],
    "eptimeline": [{"id": "1", "name": "Immediately"}, {"id": "2", "name": "As soon as possible"}]
}

# "Database" som inneholder "bruksanvisningen" for hver entitetstype.
SIMULATED_META_DATABASE = {
    "user": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": "user"},
    "people": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": "user"},
    "project": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "momstatus": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "typeofmeeting": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "unit": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "measurestate": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "location": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "meetingfrequency": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "agendastatus": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "measurepriority": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "epphase": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "epplanrole": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "epresourcecategory": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "epresourcestatus": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "epassessmentstatus": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "epscenariostatus": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "eptaskstatus": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "epscenariocategory": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "eptimeline": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None}
}

def get_entities_from_api(entity_type: str) -> list[dict] | None:
    """Simulerer GET dmaze-api.v1/entities/{entity_type}"""
    if not entity_type: return None
    print(f"  - [API SIM] GET entities for type: '{entity_type}'")
    return SIMULATED_DATABASE.get(entity_type.lower())

def get_entity_schema_from_api(entity_type: str) -> dict | None:
    """Simulerer GET dmaze-api.v1/meta/{entity_type}"""
    if not entity_type: return None
    print(f"  - [API SIM] GET metadata for type: '{entity_type}'")
    default_schema = {
        "primary_display_field": "name",
        "id_field": "id",
        "dmaze_format_wrapper": None
    }
    return SIMULATED_META_DATABASE.get(entity_type.lower(), default_schema)