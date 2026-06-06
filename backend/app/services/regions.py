"""
Region definitions and normalization for Matcha Scout.

Regions are soft tags on cafes that power filtering in the API and frontend.
They do NOT require a schema migration — old records without region fields simply
return None and are excluded from region-filtered queries.
"""
from __future__ import annotations

REGION_MAP: dict[str, str] = {
    "san-diego": "San Diego",
    "orange-county": "Orange County",
}

# ── Default locations (quick local ingestion, small sets) ─────────────────────

OC_DEFAULT_LOCATIONS: list[str] = [
    "Irvine, CA",
    "Costa Mesa, CA",
    "Garden Grove, CA",
    "Westminster, CA",
    "Orange, CA",
    "Anaheim, CA",
    "Fullerton, CA",
    "Huntington Beach, CA",
    "Newport Beach, CA",
]

SD_DEFAULT_LOCATION = "San Diego, CA"

# ── High-coverage locations (production ingestion, broader geographic spread) ─

SD_DISCOVERY_LOCATIONS: list[str] = [
    "San Diego, CA",
    "La Jolla, CA",
    "Convoy District, San Diego, CA",
    "Chula Vista, CA",
    "Del Mar, CA",
    "Encinitas, CA",
    "Carlsbad, CA",
    "Oceanside, CA",
    "Escondido, CA",
    "National City, CA",
]

OC_DISCOVERY_LOCATIONS: list[str] = [
    "Irvine, CA",
    "Costa Mesa, CA",
    "Garden Grove, CA",
    "Westminster, CA",
    "Orange, CA",
    "Anaheim, CA",
    "Fullerton, CA",
    "Huntington Beach, CA",
    "Newport Beach, CA",
    "Tustin, CA",
    "Santa Ana, CA",
    "Fountain Valley, CA",
    "Buena Park, CA",
    "Lake Forest, CA",
    "Mission Viejo, CA",
]

# ── Search term sets ──────────────────────────────────────────────────────────

# "matcha-discovery": broad sweep — catches cafes that serve matcha even if their
# primary category is not matcha. Trade-off: some irrelevant results; deduplication
# and category inspection reduce noise.
TERM_SETS: dict[str, list[str]] = {
    "matcha": ["matcha"],
    "matcha-discovery": [
        "matcha",
        "matcha latte",
        "japanese cafe",
        "tea",
        "boba matcha",
        "dessert cafe",
    ],
}


def normalize_region(region_key: str) -> tuple[str, str]:
    """Return (canonical_key, display_label) for a region identifier.

    >>> normalize_region("san-diego")
    ('san-diego', 'San Diego')
    >>> normalize_region("ORANGE-COUNTY")
    ('orange-county', 'Orange County')
    >>> normalize_region("unknown-place")
    ('unknown', 'Unknown')
    """
    key = region_key.lower().strip()
    if key in REGION_MAP:
        return key, REGION_MAP[key]
    return "unknown", "Unknown"


def get_discovery_locations(region_key: str, high_coverage: bool = False) -> list[str]:
    """Return the appropriate location list for a region."""
    if region_key == "san-diego":
        return SD_DISCOVERY_LOCATIONS if high_coverage else [SD_DEFAULT_LOCATION]
    if region_key == "orange-county":
        return OC_DISCOVERY_LOCATIONS if high_coverage else OC_DEFAULT_LOCATIONS
    return [SD_DEFAULT_LOCATION]


def get_term_set(name: str) -> list[str]:
    """Return a list of search terms for a named term set."""
    if name not in TERM_SETS:
        raise ValueError(f"Unknown term set {name!r}. Available: {list(TERM_SETS)}")
    return TERM_SETS[name]
