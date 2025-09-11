# File: src/api_simulator.py (UPDATED WITH RISK ASSESSMENT DATA)

# Denne ordboken simulerer hele Dmaze-databasen med data.
SIMULATED_DATABASE = {
    "user": [
        {"id": "user-1-ola-nordmann-uuid", "name": "Ola Nordmann", "email": "ola@example.com"},
        {"id": "user-2-kari-normann-uuid", "name": "Kari Nordmann", "email": "kari@example.com"},
        {"id": "user-3-arne-arnesen-uuid", "name": "Arne Arnesen", "email": "arne@example.com"},
        {"id": "user-4-lise-nilsen-uuid", "name": "Lise Nilsen", "email": "lise@example.com"},
        {"id": "user-5-arne-pettersen-uuid", "name": "Arne Pettersen", "email": "arne.p@example.com"},
        {"id": "user-6-ola-hansen-uuid", "name": "Ola Hansen", "email": "ola.hansen@example.com"},
    ],
    "people": [ # 'people' er et alias for 'user' og har samme data
        {"id": "user-1-ola-nordmann-uuid", "name": "Ola Nordmann", "email": "ola@example.com"},
        {"id": "user-2-kari-normann-uuid", "name": "Kari Nordmann", "email": "kari@example.com"},
        {"id": "user-3-arne-arnesen-uuid", "name": "Arne Arnesen", "email": "arne@example.com"},
        {"id": "user-4-lise-nilsen-uuid", "name": "Lise Nilsen", "email": "lise@example.com"},
        {"id": "user-5-arne-pettersen-uuid", "name": "Arne Pettersen", "email": "arne.p@example.com"},
        {"id": "user-6-ola-hansen-uuid", "name": "Ola Hansen", "email": "ola.hansen@example.com"},
    ],
    "project": [
        {"id": "2", "name": "Admin", "project_code": "PROJ-ADM-001"},
        {"id": "3", "name": "Communication", "project_code": "PROJ-COM-001"},
        {"id": "4", "name": "External/Partner", "project_code": "PROJ-EXT-001"},
        {"id": "6", "name": "HR", "project_code": "PROJ-HR-001"},
        {"id": "7", "name": "IT", "project_code": "PROJ-IT-001"},
        {"id": "8", "name": "Management", "project_code": "PROJ-MGT-001"},
        {"id": "9", "name": "Production", "project_code": "PROJ-PRO-001"},
        {"id": "5", "name": "R&D", "project_code": "PROJ-RND-001"},
        {"id": "10", "name": "Sale", "project_code": "PROJ-SAL-001"},
    ],
    "momstatus": [
        {"id": "3", "name": "Closed"},
        {"id": "1", "name": "Draft"},
        {"id": "2", "name": "Open"},
    ],
    "typeofmeeting": [
        {"id": "1", "name": "Management meeting"},
        {"id": "2", "name": "Status meeting"},
    ],
    "unit": [
        {"id": "unit-1", "name": "Finance Department"},
        {"id": "unit-2", "name": "Operations Division"},
        {"id": "unit-3", "name": "Compliance and Risk Management Unit"}
    ],
    # --- NY DATA FOR RISIKOVURDERING ---
    "assessmentstatus": [
        {"id": "3", "name": "Closed"},
        {"id": "1", "name": "Draft"},
        {"id": "2", "name": "Open"},
    ],
    "riskstatus": [
        {"id": "3", "name": "Closed"},
        {"id": "1", "name": "Draft"},
        {"id": "2", "name": "Open"},
    ],
    "consequenceprobability": [
        {"id": "2", "name": "Low: 0.1%-1% per year"},
        {"id": "4", "name": "High: 10%-50% per year"},
        {"id": "1", "name": "Very low: <0.1% per year"},
        {"id": "3", "name": "Medium: 1%-10% per year"},
        {"id": "5", "name": "Very high: >50% per year"},
    ],
    "consequenceeconomy": [
        {"id": "7", "name": "ii. Moderate - 50.000-500.000 NOK (upside)"},
        {"id": "2", "name": "2. Moderate - 50.000-500.000 NOK"},
        {"id": "5", "name": "5. Critical - > 50 MNOK"},
        {"id": "3", "name": "3. Significant - 0.5-5 MNOK"},
        {"id": "8", "name": "iii. Significant - 0.5-5 MNOK (upside)"},
    ],
    "consequencereputation": [
        {"id": "3", "name": "3. Significant - Reputation loss several key clients"},
        {"id": "4", "name": "4. Serious - Reputation loss prioritised stakeholders"},
        {"id": "5", "name": "5. Critical - National reputation loss"},
    ],
    "location": [
        {"id": "loc-1-oslo-uuid", "name": "Møterom Oslo"},
        {"id": "loc-2-bergen-uuid", "name": "Prosjektrom Bergen"},
        {"id": "loc-3-stavanger-uuid", "name": "Data Center – Stavanger"},
    ],
    "measurestate": [
        {"id": "1", "name": "Identified (pending decision)"},
        {"id": "4", "name": "In progress (not started)"},
        {"id": "12", "name": "Completed (100%) (approved)"},
    ]
}

# "Database" som inneholder "bruksanvisningen" for hver entitetstype.
SIMULATED_META_DATABASE = {
    "user": {
        "primary_display_field": "name",
        "id_field": "id",
        "dmaze_format_wrapper": "user"
    },
    "people": {
        "primary_display_field": "name",
        "id_field": "id",
        "dmaze_format_wrapper": "user"
    },
    "project": {
        "primary_display_field": "name",
        "id_field": "id",
        "dmaze_format_wrapper": None
    },
    "momstatus": {
        "primary_display_field": "name",
        "id_field": "id",
        "dmaze_format_wrapper": None
    },
    "typeofmeeting": {
        "primary_display_field": "name",
        "id_field": "id",
        "dmaze_format_wrapper": None
    },
    "unit": {
        "primary_display_field": "name",
        "id_field": "id",
        "dmaze_format_wrapper": None
    },
    # --- NY METADATA FOR RISIKOVURDERING ---
    "assessmentstatus": { "primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None },
    "riskstatus": { "primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None },
    "consequenceprobability": { "primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None },
    "consequenceeconomy": { "primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None },
    "consequencereputation": { "primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None },
    "location": { "primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None },
    "measurestate": { "primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None }
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