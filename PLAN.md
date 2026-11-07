# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

continue-implementation

## Roadmap

### core-skeleton — FastAPI/React Skeleton with Skill Registry API

Status: done

Acceptance:
- FastAPI backend runs with /health and /api/skills endpoints
- React frontend builds and displays skill list from API
- SQLite persistence for skills with search/filter
- Docker compose runs backend + frontend + Keycloak
- pytest and vitest tests pass

Implementation: `backend/app/main.py`, `backend/app/api/skills.py`, `backend/app/models/skill.py`, `backend/app/core/database.py`, `backend/app/services/skill_search.py`, `backend/requirements.txt`, `pyproject.toml`, `frontend/package.json`, `frontend/src/App.tsx`, `frontend/src/api/client.ts`, `frontend/src/components/SkillList.tsx`, `compose.yaml`

Tests: `backend/tests/test_skills.py`, `frontend/src/__tests__/SkillList.test.tsx`

### skill-registry — Full Skill CRUD with Search and Filtering

Status: done

Acceptance:
- CRUD operations work end-to-end via real HTTP boundary
- Full-text search across name, description, and tags
- Pagination with configurable page size
- Multi-column sorting
- Service-level search logic is independently unit-tested

Implementation: `backend/app/services/skill_search.py`

Tests: `backend/tests/test_skills.py`

### platform-adapters — Platform Config Generators

Status: done

Acceptance:
- Generate config JSON for Claude Code, Cursor, and OpenCode platforms
- Export workflow that downloads config as a file
- Frontend preview of generated config

Implementation: `backend/app/services/platform_config.py`, `backend/app/api/skills.py`, `frontend/src/api/client.ts`, `frontend/src/components/SkillList.tsx`

Tests: `backend/tests/test_platform_config.py`, `backend/tests/test_skills.py`

### continue-implementation — Continue implementation and resolve known failures

Status: in_progress

Acceptance:
- Run checks, fix failures, and implement the next planned feature

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
