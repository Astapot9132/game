# Repository Guidelines

## Project Structure & Module Organization
- `backend/` — FastAPI app in `app/` with subpackages `api`, `core`, `db`, `models`, `schemas`, plus Alembic migrations in `app/db/migrations`. Tests belong in `tests/` mirroring the app layout.
- `frontend/` — Vue 3 + Vite project (`src/` for components, views, stores, composables; `src/lib/api.ts` centralizes API calls). Use `tests/` for Vitest specs and `e2e/` for Playwright flows.
- `docs/` — functional specs (`api.md`, `battle_rules.md`) that drive both code and review criteria.
- `COMMUNICATION.md` — running log of decisions; update it whenever plans shift.

## Build, Test, and Development Commands
- `cd backend && poetry install` — sync Python dependencies according to `pyproject.toml`.
- `poetry run uvicorn app.main:app --reload` — start FastAPI dev server with hot reload.
- `cd frontend && npm install && npm run dev` — install JS deps and launch Vite dev server.
- `poetry run pytest` / `npm run test` — backend unit/integration tests / frontend unit tests.
- `npm run build` — type-check and bundle the frontend for production previews.

## Coding Style & Naming Conventions
- Python: Black (88 cols), isort, Ruff; prefer type hints everywhere and Pydantic models for I/O. Modules and packages in `snake_case`, classes in `CamelCase`, settings constants in `UPPER_SNAKE_CASE`.
- Vue/TypeScript: Composition API + `<script setup lang="ts">`, components in `PascalCase.vue`, composables prefixed `use`. Follow ESLint defaults from Vite and keep props/events typed.
- Config files (`.env`, `pydantic-settings`) store secrets; never hardcode credentials or JWT secrets.

## Testing Guidelines
- Backend: pytest + pytest-asyncio; place async tests beside feature under test (e.g., `tests/api/test_auth.py`). Use SQLite in-memory or transaction rollbacks for isolation. Aim for ≥80% coverage on core modules.
- Frontend: Vitest for unit/component specs (`ComponentName.spec.ts`), Playwright for e2e flows (`login.spec.ts`). Mock HTTP via MSW or Axios adapters.
- Run tests locally before opening PRs; CI should stay green.

## Commit & Pull Request Guidelines
- Use concise, action-oriented commits (`feat: add battle creation route`, `fix: correct JWT expiry`). Group unrelated changes into separate commits.
- PRs must include: summary of changes, testing evidence (`poetry run pytest`, `npm run test` outputs), linked issues/task IDs, and screenshots or GIFs for UI updates.
- Keep PRs small (<500 lines) when possible; mention follow-up work in `COMMUNICATION.md` to maintain traceability.

## Security & Configuration Tips
- Store secrets in `.env` files excluded from Git; share sample values via `.env.example`.
- Rotate JWT secrets when promoting to new environments and enforce HTTPS + secure cookies before deployment.
- For local DBs, use dedicated users/passwords per developer to limit accidental cross-environment access.
