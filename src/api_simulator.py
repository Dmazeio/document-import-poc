# This dictionary simulates the entire Dmaze database with example data.
SIMULATED_DATABASE = {
    # --- DATA FROM 'Minutes of Meeting' ---
    "user": [
        {"id": "user-1-ola-nordmann-uuid", "name": "Ola Nordmann", "email": "ola@example.com"},
        {"id": "user-2-kari-nordmann-uuid", "name": "Kari Nordmann", "email": "kari@example.com"},
        {"id": "user-3-arne-arnesen-uuid", "name": "Arne Arnesen", "email": "arne@example.com"},
        {"id": "user-4-lise-nilsen-uuid", "name": "Lise Nilsen", "email": "lise@example.com"},
        {"id": "user-5-arne-pettersen-uuid", "name": "Arne Pettersen", "email": "arne.p@example.com"},
        {"id": "user-6-ola-hansen-uuid", "name": "Ola Hansen", "email": "ola.hansen@example.com"},
        {"id": "user-7-pia-jensen-uuid", "name": "Pia Jensen", "email": "pia.jensen@example.com"},
        {"id": "user-8-jonas-fredriksen-uuid", "name": "Jonas Fredriksen", "email": "jonas.f@example.com"},
        {"id": "user-9-silje-dahl-uuid", "name": "Silje Dahl", "email": "silje.d@example.com"},
        {"id": "user-10-lise-berg-uuid", "name": "Lise Berg", "email": "lise.berg@example.com"},
        {"id": "user-11-erik-larsen-uuid", "name": "Erik Larsen", "email": "erik.l@example.com"},
    ],
    "people": [ # 'people' is an alias for 'user' and contains the same data
        {"id": "user-1-ola-nordmann-uuid", "name": "Ola Nordmann"},
        {"id": "user-2-kari-nordmann-uuid", "name": "Kari Nordmann"},
        {"id": "user-3-arne-arnesen-uuid", "name": "Arne Arnesen"},
        {"id": "user-4-lise-nilsen-uuid", "name": "Lise Nilsen"},
        {"id": "user-5-arne-pettersen-uuid", "name": "Arne Pettersen"},
        {"id": "user-6-ola-hansen-uuid", "name": "Ola Hansen"},
        {"id": "user-7-pia-jensen-uuid", "name": "Pia Jensen"},
        {"id": "user-8-jonas-fredriksen-uuid", "name": "Jonas Fredriksen"},
        {"id": "user-9-silje-dahl-uuid", "name": "Silje Dahl"},
        {"id": "user-10-lise-berg-uuid", "name": "Lise Berg"},
        {"id": "user-11-erik-larsen-uuid", "name": "Erik Larsen"},
    ],
    "project": [
        {"id": "2", "name": "Admin"}, {"id": "3", "name": "Communication"}, {"id": "4", "name": "External/Partner"},
        {"id": "6", "name": "HR"}, {"id": "7", "name": "IT"}, {"id": "8", "name": "Management"},
        {"id": "9", "name": "Production"}, {"id": "5", "name": "R&D"}, {"id": "10", "name": "Sale"},
    ],
    "momstatus": [{"id": "3", "name": "Closed"}, {"id": "1", "name": "Draft"}, {"id": "2", "name": "Open"}],
    "typeofmeeting": [{"id": "1", "name": "Management meeting"}, {"id": "2", "name": "Status meeting"}],
    "unit": [{"id": "unit-1", "name": "Finance Department"}, {"id": "unit-2", "name": "Operations Division"}],
    "measurestate": [
        {"id": "1", "name": "Identified (pending decision)"},
        {"id": "4", "name": "In progress (not started)"},
        {"id": "12", "name": "Completed (100%) (approved)"},
        {"id": "5", "name": "To be implemented (pending accept)"}
    ],
    "location": [
        {"id": "loc-1-oslo-uuid", "name": "Møterom Oslo"}, 
        {"id": "loc-2-bergen-uuid", "name": "Prosjektrom Bergen"},
        {"id": "loc-3-stavanger-uuid", "name": "Datasenter – Stavanger"}
    ],
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
    "eptimeline": [{"id": "1", "name": "Immediately"}, {"id": "2", "name": "As soon as possible"}],
    
    # --- NEW DATA FOR 'Risk Assessment' ADDED HERE ---
    "riskcategory": [
        {"id": "riskcat-1-uuid", "name": "Operational Risk"}
    ],
    "consequenceprobability": [
        {"id": "prob-1-uuid", "name": "2. Low: 0.1%-1% per year"},
        {"id": "prob-2-uuid", "name": "3. Medium: 1%-10% per year"}
    ],
    "assessmentstatus": [
        {"id": "assess-stat-1-uuid", "name": "Open"},
        {"id": "assess-stat-2-uuid", "name": "Draft"}
    ],
    "consequenceeconomy": [
        {"id": "econ-1-uuid", "name": "2. Moderate - 50.000-500.000 NOK"},
        {"id": "econ-2-uuid", "name": "3. Significant - 0.5-5 MNOK"}
    ],
    "riskstatus": [
        {"id": "riskstat-1-uuid", "name": "Draft"},
        {"id": "riskstat-2-uuid", "name": "Open"}
    ],
    "consequencereputation": [
        {"id": "rep-1-uuid", "name": "4. Serious - Reputation loss prioritised stakeholders"}
    ]
}

# Meta database containing the "instructions" (metadata) for each entity type.
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
    "eptimeline": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    
    # --- NY METADATA FOR 'Risk Assessment' LAGT TIL HER ---
    "riskcategory": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "consequenceprobability": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "assessmentstatus": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "consequenceeconomy": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "riskstatus": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None},
    "consequencereputation": {"primary_display_field": "name", "id_field": "id", "dmaze_format_wrapper": None}
}

def get_entities_from_api(entity_type: str) -> list[dict] | None:
    """Simulates GET dmaze-api.v1/entities/{entity_type}"""
    if not entity_type: return None
    print(f"  - [API SIM] GET entities for type: '{entity_type}'")
    return SIMULATED_DATABASE.get(entity_type.lower())

def get_entity_schema_from_api(entity_type: str) -> dict | None:
    """Simulates GET dmaze-api.v1/meta/{entity_type}"""
    if not entity_type: return None
    print(f"  - [API SIM] GET metadata for type: '{entity_type}'")
    default_schema = {
        "primary_display_field": "name",
        "id_field": "id",
        "dmaze_format_wrapper": None
    }
    return SIMULATED_META_DATABASE.get(entity_type.lower(), default_schema)