import re

# Synonym groups for CAS actions
SYNONYM_MAP = {
    'delete': ['delete', 'remove', 'removes', 'deleted'],
    'visible': ['visible', 'display', 'displayed', 'show', 'shown'],
    'reject': ['reject', 'declined', 'decline'],
    'add': ['add', 'create', 'creates'],
    'submit': ['submit', 'save', 'saves', 'saved'],
    'approve': ['approve', 'sanction', 'approved'],
    'edit': ['edit', 'update', 'updated', 'updates'],
    'open': ['open', 'opens', 'navigate', 'navigates'],
    'verify': ['verify', 'validate', 'validates'],
    'select': ['select', 'choose', 'chooses'],
    'start': ['start', 'initiate', 'initiates'],
    'pending': ['pending', 'hold', 'held'],
    'checked': ['checked', 'check', 'unchecked'],
    'disabled': ['disabled', 'readonly'],
}


def normalise_query_text(query: str) -> str:
    """Normalize raw query text."""
    if not query:
        return ""
    # Remove step keywords
    text = re.sub(r'^(Given|When|Then|And|But)\s+', '', query, flags=re.IGNORECASE)
    return text.strip().lower()


def expand_for_vector(query: str) -> str:
    """Expand query with synonyms for FAISS embedding."""
    normalized = normalise_query_text(query)
    if not normalized or len(normalized.split()) > 10:
        return normalized

    expanded = [normalized]
    for key, synonyms in SYNONYM_MAP.items():
        if key in normalized.lower():
            expanded.extend(synonyms[:3])

    return ' '.join(expanded)


def expand_for_fts(query: str) -> str:
    """Expand query for PostgreSQL FTS."""
    normalized = normalise_query_text(query)
    if not normalized:
        return normalized

    expanded = [normalized]
    for key, synonyms in SYNONYM_MAP.items():
        if key in normalized.lower():
            expanded.extend(synonyms[:3])

    return ' | '.join(expanded)


def expand_for_trigram(query: str) -> str:
    """Expand query for trigram matching."""
    normalized = normalise_query_text(query)
    if not normalized or len(normalized.split()) > 10:
        return normalized

    expanded = [normalized]
    for key, synonyms in SYNONYM_MAP.items():
        if key in normalized.lower():
            expanded.extend(synonyms[:3])

    return ' '.join(expanded)
