# File: src/tools.py (NY FIL)

# Dette er den ENESTE kilden til sannhet for brukerdata.
# Nøkler er med små bokstaver for å sikre case-insensitivt oppslag.
USER_DATABASE = {
    "ola nordmann": "user-1-ola-nordmann-uuid",
    "kari nordmann": "user-2-kari-normann-uuid",
    "arne arnesen": "user-3-arne-arnesen-uuid",
    "lise nilsen": "user-4-lise-nilsen-uuid",
    "arne pettersen": "user-5-arne-pettersen-uuid",
    "ola hansen": "user-6-ola-hansen-uuid",
}

def find_user_id_by_name(full_name: str) -> str | None:
    """
    Performs a case-insensitive, deterministic lookup for a user's ID.
    Returns the ID string on an exact match, otherwise returns None.
    """
    if not isinstance(full_name, str):
        return None

    print(f"  - [LOOKUP] Performing lookup for: '{full_name}'")
    lookup_name = full_name.lower().strip()
    user_id = USER_DATABASE.get(lookup_name)
    
    if user_id:
        print(f"  - [LOOKUP RESULT] Found match: {user_id}")
    else:
        print(f"  - [LOOKUP RESULT] No match found for '{full_name}'.")
    
    return user_id