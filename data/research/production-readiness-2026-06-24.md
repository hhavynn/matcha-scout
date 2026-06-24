# Matcha Scout production readiness — 2026-06-24

## Recommendation

**GO after explicit authorization, using the documented deployment order.**

The read-only Neon reconciliation exactly matches the approved expected plan,
has no blocked operations, and produced a verified backup. Production has not
been modified by this readiness work.

## Read-only production reconciliation

| Check | Result |
|---|---:|
| Production cafés | 54 |
| Production drinks before release | 92 |
| Café IDs matching local | 54 / 54 |
| Report cafés matched | 44 / 44 |
| Café creates | 0 |
| Café metadata updates | 13 |
| Drink creates | 10 |
| Drink evidence updates | 18 |
| Production soft exclusions | 2 |
| Blocked operations | 0 |
| Expected-count drift | 0 |
| Duplicate normalized café names | 0 |
| Duplicate normalized drink names within a café | 0 |
| Address conflicts | 0 |
| Taste profiles imported | 0 |
| External ratings imported | 0 |

Risk level reported by the reconciliation: **low**.

## Exact café writes

- Labora
- Little While
- Bopomofo Cafe
- Matcha Cafe Maiko
- Lovesong Coffee
- Communal (North Park record)
- Mostra Coffee (Hillcrest record)
- Rikka Fika
- Flour Atelier
- Selva Coffee House (Midway record)
- Chance’s Coffee
- Urban Matcha — uncertainty status/note only
- J.sweets San Diego — correct the existing combined display identity while preserving its internal ID

## Exact drink creates

Labora:

- Banana 53
- Scarlet 3
- Blueberry 30
- Pandan 32
- Pistachio 54
- Ube 39

Bopomofo Cafe:

- Carrot Matcha Latte
- Matcha Latte
- Matcha Soda
- Mint Matcha Latte

All created drinks receive deterministic IDs and a neutral `review_count: 0`
profile. Neutral profiles remain excluded from recommendations.

## Exact drink evidence refreshes

- Labora: LABORA 1, Vienna Matcha, Earl 37, Matcha X2
- Little While: Matcha Latte, LW Matcha Latte, Matcha + Coconut Water, Matcha Ceremony Set
- Bopomofo Cafe: Ba-La Matcha
- Lovesong Coffee: Lazy Sunday, Pool Party!!!, King of the Jungle, Twisted Sister, Maui Babe, Double Down, Bee, Evergreen Parke, WildChild, Bodhi Boy

Existing production drink IDs are preserved.

## Soft exclusions

- Bopomofo Cafe — Triple Strawberry Matcha
- Bopomofo Cafe — Blueberry Matcha Latte

Both are admin-curated, have zero review items, and have neutral profiles with
`review_count: 0`. Production uses metadata soft exclusion; no partition is
deleted.

## Review and taste-profile safety

The backup contains 43 affected partitions:

- 20 existing taste-profile records
- 0 affected Matcha Scout review items
- 0 affected profiles with real reviews

The plan updates drink metadata only. It does not write existing taste-profile
or review records. Rollback blocks deletion of any newly created drink that gains
a review after release.

## Backup and rollback

Verified read-only preflight backup:

`data/backups/deep-research-production-20260624T171114Z.json`

Machine-readable reconciliation:

`data/backups/reconciliation-production-20260624T171114Z.json`

Both files parsed successfully and passed a credential-pattern scan. They are
gitignored.

Rollback commands and limitations are documented in:

`docs/production-release-runbook.md`

## Local versus production

- Café IDs are identical across local and production.
- Local has the ten planned strict drink additions.
- Production has the two records planned for soft exclusion.
- Local also has one unrelated, pre-existing Maiko `Strawberry Matcha Latte`
  that is not in production and is not part of this release.
- No production-only duplicate names were found.

## Resolved source questions

- **Little While hours:** current official site lists Monday–Thursday 7am–2pm and Friday–Sunday 7am–4pm.
- **J.sweets / YAMARI:** official J.sweets locations list San Diego inside Mitsuwa; official YAMARI locations list Torrance and Cypress, not San Diego. Preserve the internal ID and label it J.sweets San Diego.

## Remaining manual conflicts

- **Urban Matcha:** the official site does not currently establish a San Diego
  location, while the existing record has a Convoy address. Keep status
  `uncertain`; do not remove or mark open.
- **Matcha Cafe Maiko:** the official chain menu says availability varies by
  store. Keep the 17 chain-menu items withheld until the San Diego store confirms
  them.

These do not block the unrelated verified release operations.

## Deployment order

1. Deploy backend support for nullable prices and soft exclusions.
2. Deploy frontend support for nullable prices and status notes.
3. Re-run read-only Neon reconciliation and create a fresh backup.
4. Apply the guarded production sync.
5. Verify API responses, pages, review counts, taste profiles, and Vercel logs.

No deploy or production apply has been performed during readiness preparation.
