# This dictionary simulates the entire Dmaze database with example data.
SIMULATED_DATABASE = {

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
    "people": [
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
        {"id": "proj-2-admin-uuid", "name": "Admin"}, {"id": "proj-3-comm-uuid", "name": "Communication"}, {"id": "proj-4-ext-uuid", "name": "External/Partner"},
        {"id": "proj-6-hr-uuid", "name": "HR"}, {"id": "proj-7-it-uuid", "name": "IT"}, {"id": "proj-8-mgmt-uuid", "name": "Management"},
        {"id": "proj-9-prod-uuid", "name": "Production"}, {"id": "proj-5-rd-uuid", "name": "R&D"}, {"id": "proj-10-sale-uuid", "name": "Sale"},
    ],
    "momstatus": [{"id": "momstat-3-closed-uuid", "name": "Closed"}, {"id": "momstat-1-draft-uuid", "name": "Draft"}, {"id": "momstat-2-open-uuid", "name": "Open"}],
    "typeofmeeting": [{"id": "meettype-1-mgmt-uuid", "name": "Management meeting"}, {"id": "meettype-2-status-uuid", "name": "Status meeting"}],
    "unit": [{"id": "unit-1-finance-uuid", "name": "Finance Department"}, {"id": "unit-2-ops-uuid", "name": "Operations Division"}],
    "measurestate": [
        {"id": "mstate-1-identified-uuid", "name": "Identified (pending decision)"},
        {"id": "mstate-4-inprogress-uuid", "name": "In progress (not started)"},
        {"id": "mstate-12-completed-uuid", "name": "Completed (100%) (approved)"},
        {"id": "mstate-5-implement-uuid", "name": "To be implemented (pending accept)"}
    ],
    "location": [
        {"id": "loc-1-oslo-uuid", "name": "Møterom Oslo"}, 
        {"id": "loc-2-bergen-uuid", "name": "Prosjektrom Bergen"},
        {"id": "loc-3-stavanger-uuid", "name": "Datasenter – Stavanger"}
    ],
    "meetingfrequency": [{"id": "meetfreq-2-oneoff-uuid", "name": "One-off"}, {"id": "meetfreq-1-recurring-uuid", "name": "Recurring"}],
    "agendastatus": [{"id": "agendastat-3-closed-uuid", "name": "Closed"}, {"id": "agendastat-1-draft-uuid", "name": "Draft"}, {"id": "agendastat-2-open-uuid", "name": "Open"}],
    "measurepriority": [{"id": "mprio-1-high-uuid", "name": "High"}, {"id": "mprio-3-low-uuid", "name": "Low"}, {"id": "mprio-2-medium-uuid", "name": "Medium"}],

    "epphase": [{"id": "epphase-3-norm-uuid", "name": "Normalisation"}, {"id": "epphase-1-mob-uuid", "name": "Notification and mobilisation"}, {"id": "epphase-2-handling-uuid", "name": "Handling"}],
    "epplanrole": [{"id": "eprole-3-firelead-uuid", "name": "Fire response leader"}, {"id": "eprole-1-emgmt-uuid", "name": "Emergency manager"}],
    "epresourcecategory": [{"id": "eprescat-1-coop-uuid", "name": "Cooperative partner"}, {"id": "eprescat-2-comp-uuid", "name": "Competence"}, {"id": "eprescat-3-manning-uuid", "name": "Manning"}, {"id": "eprescat-4-equip-uuid", "name": "Equipment"}],
    "epresourcestatus": [{"id": "epresstat-5-notrel-uuid", "name": "Not relevant"}, {"id": "epresstat-1-ident-uuid", "name": "Identified"}, {"id": "epresstat-2-prepared-uuid", "name": "Part of today's preparedness"}],
    "epassessmentstatus": [{"id": "epassess-3-closed-uuid", "name": "Closed"}, {"id": "epassess-1-draft-uuid", "name": "Draft"}, {"id": "epassess-2-open-uuid", "name": "Open"}],
    "epscenariostatus": [{"id": "epscenstat-1-ident-uuid", "name": "Identified"}, {"id": "epscenstat-3-notanalysed-uuid", "name": "Not analysed"}, {"id": "epscenstat-2-analysed-uuid", "name": "Analysed"}],
    "eptaskstatus": [{"id": "eptaskstat-1-ident-uuid", "name": "Identified"}, {"id": "eptaskstat-2-prepared-uuid", "name": "Part of today's preparedness"}],
    "epscenariocategory": [{"id": "epscencat-1-natural-uuid", "name": "Natural event"}, {"id": "epscencat-2-fire-uuid", "name": "Fire event"}],
    "eptimeline": [{"id": "eptime-1-immediate-uuid", "name": "Immediately"}, {"id": "eptime-2-asap-uuid", "name": "As soon as possible"}],
    
    "riskcategory": [
        {"id": "riskcat-1-operational-uuid", "name": "Operational Risk"}
    ],
    "consequenceprobability": [
        {"id": "prob-1-low-uuid", "name": "2. Low: 0.1%-1% per year"},
        {"id": "prob-2-medium-uuid", "name": "3. Medium: 1%-10% per year"}
    ],
    "assessmentstatus": [
        {"id": "assess-stat-1-open-uuid", "name": "Open"},
        {"id": "assess-stat-2-draft-uuid", "name": "Draft"}
    ],
    "consequenceeconomy": [
        {"id": "econ-1-moderate-uuid", "name": "2. Moderate - 50.000-500.000 NOK"},
        {"id": "econ-2-significant-uuid", "name": "3. Significant - 0.5-5 MNOK"}
    ],
    "riskstatus": [
        {"id": "riskstat-1-draft-uuid", "name": "Draft"},
        {"id": "riskstat-2-open-uuid", "name": "Open"}
    ],
    "consequencereputation": [
        {"id": "rep-1-serious-uuid", "name": "4. Serious - Reputation loss prioritised stakeholders"}
    ]
}


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