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

# Default Yelp search locations for Orange County multi-city ingestion.
# Searching across cities gives better coverage than "Orange County, CA" alone.
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
