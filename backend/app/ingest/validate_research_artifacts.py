"""Validate committed Deep Research JSON without accessing a database."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return payload


def validate(cafes_path: Path, drinks_path: Path) -> list[str]:
    errors: list[str] = []
    cafes = load(cafes_path)
    drinks = load(drinks_path)

    cafe_rows = cafes.get("cafes")
    drink_rows = drinks.get("drinks")
    if not isinstance(cafe_rows, list):
        errors.append("Cafe artifact must contain a cafes array.")
        cafe_rows = []
    if not isinstance(drink_rows, list):
        errors.append("Drink artifact must contain a drinks array.")
        drink_rows = []

    if len(cafe_rows) != 44:
        errors.append(f"Expected 44 cafe concepts, found {len(cafe_rows)}.")
    if len(drink_rows) != 28:
        errors.append(f"Expected 28 strict drinks, found {len(drink_rows)}.")

    cafe_ids = [row.get("cafe_id") for row in cafe_rows]
    if None in cafe_ids or len(cafe_ids) != len(set(cafe_ids)):
        errors.append("Cafe IDs must be present and unique.")

    drink_keys: set[tuple[str, str]] = set()
    for index, row in enumerate(drink_rows, start=1):
        label = f"Drink #{index}"
        key = (row.get("cafe_id", ""), row.get("name", "").casefold())
        if not all(key):
            errors.append(f"{label} requires cafe_id and name.")
        elif key in drink_keys:
            errors.append(f"{label} duplicates {row.get('name')} at {row.get('cafe_id')}.")
        drink_keys.add(key)
        if row.get("verification_source") != "official_menu":
            errors.append(f"{label} must use official_menu verification.")
        if not row.get("verification_url"):
            errors.append(f"{label} requires verification_url.")
        if not row.get("verified_at"):
            errors.append(f"{label} requires verified_at.")
        price = row.get("price")
        if price is not None and (not isinstance(price, (int, float)) or price <= 0):
            errors.append(f"{label} price must be null or positive.")
        for field in ("is_hot", "is_iced"):
            if row.get(field) is not None and not isinstance(row[field], bool):
                errors.append(f"{label} {field} must be boolean or null.")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cafes", type=Path)
    parser.add_argument("drinks", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors = validate(args.cafes, args.drinks)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Research artifacts are valid: 44 cafes, 28 strict drinks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
