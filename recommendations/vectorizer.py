"""Feature preparation kept separate from request-handling code."""
def apartment_text(apartment):
    return f"{apartment.location} {' '.join(apartment.amenities or [])}"

def preference_text(preference):
    return f"{preference.preferred_location} {' '.join(preference.amenities_wanted or [])}"
