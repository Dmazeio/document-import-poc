# File: src/tools.py (COMPLETE VERSION WITH ATTENDEES SUPPORT)

import re

# The ONLY source of truth for user data.
# Keys are lowercase for case-insensitive lookup.
USER_DATABASE = {
    "ola nordmann": "user-1-ola-nordmann-uuid",
    "kari nordmann": "user-2-kari-normann-uuid",
    "arne arnesen": "user-3-arne-arnesen-uuid",
    "lise nilsen": "user-4-lise-nilsen-uuid",
    "arne pettersen": "user-5-arne-pettersen-uuid",
    "ola hansen": "user-6-ola-hansen-uuid",
    "silje dahl": "user-7-silje-dahl-uuid",  
    "erik larsen": "user-8-erik-larsen-uuid",  
    "lise berg": "user-9-lise-berg-uuid",  
    "jonas fredriksen": "user-10-jonas-fredriksen-uuid",  
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

def find_user_ids_from_text(attendees_text: str) -> list[str]:
    """
    Parses a text string containing multiple attendee names and returns a list of user IDs.
    Handles various formats like comma-separated, newline-separated, etc.
    """
    if not isinstance(attendees_text, str):
        return []
    
    print(f"  - [ATTENDEES LOOKUP] Parsing attendees text: '{attendees_text}'")
    
    # Split by common delimiters: comma, semicolon, newline, "and", "og"
    names = re.split(r'[,;\n]|(?:\s+og\s+)|(?:\s+and\s+)', attendees_text)
    
    user_ids = []
    for name in names:
        # Clean up the name - remove extra whitespace, parentheses content, etc.
        cleaned_name = re.sub(r'\([^)]*\)', '', name).strip()
        if cleaned_name:
            user_id = find_user_id_by_name(cleaned_name)
            if user_id:
                user_ids.append(user_id)
    
    print(f"  - [ATTENDEES RESULT] Found {len(user_ids)} valid attendees: {user_ids}")
    return user_ids