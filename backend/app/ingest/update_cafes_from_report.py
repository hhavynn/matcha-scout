"""Deprecated June 23 report sync.

The audited June 24 workflow supersedes this prototype. It is retained only so
old notes and commands fail safely instead of silently targeting a database.
"""
from __future__ import annotations

import sys


def main() -> int:
    print(
        "ERROR: update_cafes_from_report is retired. "
        "Use app.ingest.sync_deep_research and follow "
        "docs/production-release-runbook.md.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
