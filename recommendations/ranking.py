def match_reasons(apartment, preference):
    reasons = []
    if preference.min_price is None or preference.max_price is None or preference.min_price <= apartment.price <= preference.max_price:
        reasons.append("Budget")
    if not preference.preferred_location or apartment.location == preference.preferred_location:
        reasons.append("Location")
    if apartment.bedrooms >= preference.min_bedrooms:
        reasons.append("Bedroom requirement")
    if set(preference.amenities_wanted or []).intersection(apartment.amenities or []):
        reasons.append("Preferred amenities")
    return reasons
