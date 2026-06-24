# San Diego Matcha Deep Research audit — 2026-06-24

## Scope and limitations

The Markdown report was treated as research input, not as an authoritative import. Its linked JSON, CSV, and chart files were not present in the attachment or Downloads folder. The audit therefore reconstructs only facts stated in the report and checks the strict drink subset against the cited official menu pages.

Primary menu sources used:

- [Labora official menu](https://laboracafe.com/menu)
- [Little While official menu](https://www.littlewhilesd.com/menu)
- [Bopomofo official menu](https://www.bopomofocafe.com/menu)
- [Matcha Cafe Maiko official menu](https://www.matchacafe-maiko.com/eng/menu/)
- [Lovesong official menu](https://www.lovesongcoffee.com/lovesong-menu)

No Google, Yelp, or Beli rating was imported from this report. No external rating or menu description was converted into a Matcha Scout taste profile.

## Import decision summary

| Classification | Cafés | Drinks |
|---|---:|---:|
| Verified | 4 | 28 |
| Partially verified | 7 | 17 Maiko chain-menu items withheld |
| Unverified | 31 | 0 |
| Conflicting | 1 | 0 |
| Excluded | — | 3 named records/findings |

The report says the strict file contains 29 drinks. The current evidence supports **28**:

- Labora: 10
- Little While: 4
- Bopomofo Cafe: 5, all with unknown public prices
- Lovesong Coffee: 9

## Verified drink changes

- **10 new local records proposed:** six Labora flavor builds and four current Bopomofo drinks.
- **18 existing local records proposed for evidence refresh:** four Labora, four Little While, one Bopomofo, and nine Lovesong drinks.
- Unknown Bopomofo prices remain `null`.
- New drinks receive neutral placeholder profiles with `review_count: 0`; recommendations ignore those profiles until a Matcha Scout review exists.

## Exclusions and corrections

| Record | Decision | Reason |
|---|---|---|
| Lovesong — Matcha Stewart | Excluded | Appears in the report's condensed table but not on the current official Top Shelf Matcha menu. |
| Bopomofo — Triple Strawberry Matcha | Excluded from strict current catalog | It is a seasonal homepage feature, not a current Premium Matcha menu item. |
| Bopomofo — Blueberry Matcha Latte | Excluded | Not supported by the current official menu or the new report's strict subset. |
| Matcha Cafe Maiko — 17 chain items | Withheld / partially verified | Official menu warns that availability varies by store; San Diego-specific confirmation is required. |

The two Bopomofo exclusions may be removed locally only when the records are admin-curated and have no Matcha Scout reviews. User reviews and taste profiles are never deleted.

## Café metadata updates

Thirteen existing café records have safe additive local metadata updates. Eleven receive source-backed listing/menu metadata, while the two conflict records receive only an `uncertain` badge and explanatory note:

- Labora
- Little While
- Bopomofo Cafe
- Matcha Cafe Maiko
- Lovesong Coffee
- Communal (North Park)
- Mostra Coffee (Hillcrest)
- Rikka Fika
- Flour Atelier
- Selva Coffee House (Midway)
- Chance’s Coffee
- Urban Matcha — uncertainty note only
- J.sweets San Diego — corrected identity using the official locations page

No new café is auto-created because all 44 reconstructed report concepts match an existing local record.

## Unverified follow-up set

The following records remain matched but receive no new menu assertions:

12 Hrs Matcha Cafe, Galu Cafe and Delicatessen, Cafe Alessie, Easy Does It, Gotcha Tea, Tori Cafe, Boba Religion, ESSNTL Coffee, Camellia Rd Tea Bar, KAFE'SITO, The Barista Botanist, Hatsuzakura, The Cakery Cafe, Hydout Cafe, Marta, Cristallo Cafe, Cafe 88, Casa De Otay, Yaqui Coffee House, Nomade, Friends of Friends, Despertar Coffee, Drift Cafe, Forum Coffee, Morning Dew, Kubo Coffee, Kaphe Muna, Hey Midori, Prosperitea, Holy Matcha, and Kyoto Coast Matcha.

## Conflicts requiring manual review

1. **Urban Matcha:** reconcile the report's upcoming claim with the existing Convoy-address record using a current official source.
2. **Communal, Mostra, and Selva:** continue matching by exact location, not brand name alone.

Resolved during release preflight:

- **J.sweets / YAMARI:** the official locations page lists J.sweets San Diego inside Mitsuwa and lists YAMARI only in Torrance and Cypress. Preserve the existing internal ID but rename the record to J.sweets San Diego.
- **Little While hours:** the official site currently lists Monday–Thursday 7am–2pm and Friday–Sunday 7am–4pm.

## Schema and UX findings

- Prices must be nullable; `$0.00` is not a valid substitute for unknown.
- Drinks now preserve a verification date.
- Cafés can show business status and a short status/conflict note.
- Unrated neutral taste profiles are no longer recommendation inputs.
- Yelp and Beli remain separately labeled; the report added neither.

## Local reconciliation outcome

Dry-run result before local apply:

- Cafés matched: 44
- Cafés added: 0
- Cafés proposed for metadata update: 13
- Drinks proposed for creation: 10
- Drinks proposed for update: 18
- Existing excluded drinks eligible for safe local removal: 2
- Research conflicts requiring review: 1
- Missing or ambiguous café matches: 0

Production is explicitly out of scope for this workflow.
