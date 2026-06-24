# San Diego café match report — 2026-06-24

Source: `deep-research-report (1).md`

The report's linked machine-readable exports were not attached, so the 44-concept set was reconstructed from the report text. Every reconstructed concept matched one existing local café by internal ID. Address checks were required for the 11 records selected for metadata updates.

## Result

| Result | Count |
|---|---:|
| Report concepts | 44 |
| Matched to existing cafés | 44 |
| New cafés required | 0 |
| Metadata updates proposed | 13 |
| Unchanged/unverified matches | 31 |
| Low-confidence automatic matches | 0 |
| Address conflicts | 0 |
| Research conflicts requiring manual review | 1 |

## Metadata update matches

| Report café | Internal café ID | Match evidence |
|---|---|---|
| Labora | `yelp-dqrcwtf6575theg7r5vdfg` | Internal ID + exact address |
| Little While | `yelp-qwvdx0h1yqweolvegpnfna` | Internal ID + exact address |
| Bopomofo Cafe | `yelp-pixshlytcxxnrh3veczjba` | Internal ID + exact address |
| Matcha Cafe Maiko | `yelp-atxbqaz7yllcmxljoqiwcw` | Internal ID + exact address |
| Lovesong Coffee | `yelp-snziucfu61i7lwcg7o0zga` | Internal ID + exact address |
| Communal (North Park) | `yelp-iykfvpgkbrkju8-ueoweaa` | Internal ID + exact address |
| Mostra Coffee (Hillcrest) | `yelp-hk5urmoqp0tm2oqkwaxgqg` | Internal ID + exact address |
| Rikka Fika | `yelp-w5jokeeoj5qejdmaztou3w` | Internal ID + exact address |
| Flour Atelier | `custom-flour-atelier` | Internal ID + exact address |
| Selva Coffee House (Midway) | `yelp-44znqntb4zho4dhchrdjsa` | Internal ID + exact address |
| Chance’s Coffee | `yelp-bv40bfy-xgxljz2cqoyfya` | Internal ID + exact address |
| Urban Matcha | `yelp-iovtfdskgvm6sdapvlpsow` | Internal ID; marked uncertain without selecting either conflicting status |
| J.sweets San Diego | `custom-jsweets-yamari` | Internal ID + exact address; official location list resolves the prior combined-vendor ambiguity |

## Research conflicts — no automatic merge or status change

- **Urban Matcha:** the report describes the concept as upcoming from secondary reporting, while the existing local record has a Convoy address. A current primary-source check is required before changing its status.
- **J.sweets / YAMARI resolution:** J.sweets officially lists San Diego inside Mitsuwa. YAMARI's official locations list Torrance and Cypress, not San Diego. The existing ID is preserved and its display name is corrected to J.sweets San Diego.

## Multi-location safeguards

- Communal was matched only to the existing North Park address.
- Mostra was matched only to the existing Hillcrest address.
- Selva Midway remains separate from the report's upcoming Del Mar location.
- No chain-wide or brand-level record was merged across physical locations.
