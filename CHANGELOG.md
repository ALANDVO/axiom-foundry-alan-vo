# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-10-15

### Added
- FastAPI backend with SQLite persistence and SQLAlchemy ORM
- Skill registry API: create, read, update, delete, search, filter, pagination, sorting
- React frontend with TypeScript and Vite: skill browsing, search, filtering, detail view
- Typed API client derived from backend response envelopes
- Docker Compose orchestration with PostgreSQL for Keycloak
- Keycloak realm configuration with viewer/operator/admin roles
- Environment configuration template (`.env.example`)
- Backend and frontend tests (pytest + vitest)
- Dockerfiles with nonroot users and healthchecks

### Known Limitations
- Authentication (OIDC/Keycloak) integration is planned but not yet implemented
- LLM adapter layer is not yet implemented; configuration variables are present for future use