# Workspace Agent Rules

## Task Delegation & Subagent Usage

- **Proactively Use Subagents**: Do not perform all backend, database, frontend, AI parsing, or QA tasks in the main parent conversation. You **MUST** delegate specialized tasks to the appropriate subagents:
  * `frontend-expert` — for Next.js, React 19, styling, and user-facing features.
  * `backend-expert` — for FastAPI endpoints, routing, and ingestion client logic.
  * `database-expert` — for PostgreSQL, migrations, and Neon database schema setups.
  * `ai-integration` — for LLM prompt engineering, Gemini API validation, and structured parsing.
  * `qa-devops` — for pytest execution, lint checks, docker compose, and Vercel/kind verification.
  
- **Parallel Execution**: Leverage concurrent subagent runs to handle complex multi-file features or independent tasks simultaneously.
- **Unified Context**: Share details, documentation URLs, and schemas when prompting subagents to ensure they operate with full alignment on the workspace state.
