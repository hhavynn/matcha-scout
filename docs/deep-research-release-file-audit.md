# Deep Research milestone file audit

## Release scope

The active release path is:

- `backend/app/ingest/sync_deep_research.py`
- `backend/app/ingest/rollback_deep_research.py`
- `backend/app/ingest/validate_research_artifacts.py`
- `data/research/sd-matcha-*`
- nullable-price, verification, status, and catalog-visibility model/API/UI changes
- production-sync safety tests
- `.github/workflows/ci.yml`

## Earlier scripts not part of this release

These untracked scripts predate the guarded release workflow and should not be
included in a future milestone commit without separate review:

- `backend/app/ingest/delete_yamari.py`
  - Destructive direct SQL.
  - Prints the complete database URL.
  - No dry-run or target confirmation.
- `backend/app/ingest/ingest_custom_cafes.py`
  - Prints the complete database URL.
  - Writes immediately and has no dry-run/apply gate.
- `backend/app/ingest/ingest_manual_custom_spots.py`
  - Attempts local and production writes in one invocation.
  - Loads dotenv files manually.
  - No typed production confirmation.
- `backend/app/ingest/ingest_popups.py`
  - Attempts local and production writes in one invocation.
  - Fetches external data and writes it immediately.
- `backend/app/ingest/update_cafes_from_report.py`
  - Earlier June 23 reconciliation prototype, now replaced by a fail-closed
    compatibility stub pointing to the audited June 24 workflow.

They have not been deleted because the working tree may contain user-owned work.
The recommendation is to archive or remove them in a separately authorized
cleanup after confirming they are no longer needed.

## Secrets and exports

- No committed file contains the production connection string.
- `data/backups/` is gitignored except its documentation.
- Existing `data/curation/*.local.*` and private JSON exports remain ignored.
- Production reconciliation reports contain records and sanitized host metadata,
  but no credentials.
