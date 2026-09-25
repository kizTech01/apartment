"""Reusable, independently testable content-based recommendation service."""
from apartments.models import Apartment
from .ranking import match_reasons
from .vectorizer import apartment_text, preference_text

def recommend_apartments(tenant, limit=10):
    apartments = list(Apartment.objects.filter(status=Apartment.Status.AVAILABLE).select_related("landlord").prefetch_related("images"))
    preference = getattr(tenant, "preference", None)
    if not preference or not apartments:
        return []
    try:
        import numpy as np
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.preprocessing import MinMaxScaler
        vectorizer = TfidfVectorizer()
        text_matrix = vectorizer.fit_transform([apartment_text(a) for a in apartments] + [preference_text(preference)])
        text_scores = cosine_similarity(text_matrix[-1], text_matrix[:-1]).flatten()
        target_price = float(preference.max_price or max(a.price for a in apartments))
        prices = np.array([float(a.price) for a in apartments] + [target_price]).reshape(-1, 1)
        bedrooms = np.array([a.bedrooms for a in apartments] + [preference.min_bedrooms]).reshape(-1, 1)
        numerical = MinMaxScaler().fit_transform(np.hstack((prices, bedrooms)))
        numeric_scores = 1 - (abs(numerical[:-1, 0] - numerical[-1, 0]) + abs(numerical[:-1, 1] - numerical[-1, 1])) / 2
        scores = .65 * text_scores + .35 * numeric_scores
        ranked = sorted(zip(apartments, scores), key=lambda row: row[1], reverse=True)[:limit]
        return [{"apartment": a, "score": round(float(max(0, min(1, score))) * 100), "reasons": match_reasons(a, preference)} for a, score in ranked]
    except ImportError:
        ranked = [{"apartment": a, "score": round(100 * len(match_reasons(a, preference)) / 4), "reasons": match_reasons(a, preference)} for a in apartments]
        return sorted(ranked, key=lambda row: row["score"], reverse=True)[:limit]
