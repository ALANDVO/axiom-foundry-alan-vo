# Architecture

## Overview

Axiom Foundry is a full-stack application for managing AI coding agent skills. The backend is a FastAPI application with SQLite persistence; the frontend is a React/TypeScript single-page application built with Vite.

## Components

### Backend (`backend/`)

| Module | Responsibility |
|--------|---------------|
| `app/main.py` | FastAPI application entrypoint with lifespan-managed database initialization |
| `app/api/skills.py` | REST route handlers for skill CRUD, search, filtering, and metadata endpoints |
| `app/models/skill.py` | SQLAlchemy model defining the Skill table schema |
| `app/core/database.py` | Database engine, session factory, and dependency injection |
| `app/services/skill_search.py` | Deterministic search and filter query builder |
| `app/services/__init__.py` | Service package exports |

### Frontend (`frontend/`)

| Module | Responsibility |
|--------|---------------|
| `src/main.tsx` | React entry point |
| `src/App.tsx` | Root component with skill list and detail view |
| `src/api/client.ts` | Typed API client with typed response envelopes |
| `src/components/SkillList.tsx` | Skill browsing, search, filtering, and pagination |
| `src/App.css` | Application styles |
| `src/test-setup.ts` | Vitest setup and API mocking |

## Data Flow

1. User interacts with the React frontend in the browser.
2. Frontend API client sends HTTP requests to FastAPI backend.
3. FastAPI routes map requests to route handlers.
4. Route handlers use SQLAlchemy sessions (injected via `get_db` dependency) to query or mutate the SQLite database.
5. Search/filter logic is encapsulated in `app.services.skill_search`.
6. Route handlers return Pydantic response models that serialize ORM objects to JSON.
7. Frontend receives JSON and updates the UI.

## Persistence

- SQLite database with SQLAlchemy 2.x ORM.
- `DATABASE_URL` environment variable controls the database location.
- Tables are created automatically on application startup via the lifespan handler.
- The `Skill` model has indexes on `name`, `category`, `platform`, and `capability` for efficient filtering.

## Future Architecture (Planned)

- **Authentication**: OIDC authorization-code flow through Keycloak with PKCE and SameSite cookie sessions.
- **Authorization**: Role-based access control (viewer, operator, admin) enforced on all data endpoints.
- **LLM adapter layer**: Pluggable adapters for OpenAI-compatible, Anthropic, Gemini, and Ollama providers.
- **Platform adapters**: Config generators for Claude Code, Codex, Cursor, OpenCode, Gemini, and Zed.

## Deployment

```
                    ┌─────────────────────────────────┐
                    │        Reverse Proxy (TLS)       │
                    │       (nginx/Caddy/Cloud)        │
                    └────┬──────────────┬──────────────┘
                         │              │
              ┌──────────▼──┐  ┌────────▼──────────┐
              │  Frontend   │  │     Backend       │
              │  (nginx)    │  │  (FastAPI)        │
              └─────────────┘  └──────┬────────────┘
                                      │
                         ┌────────────▼──────────┐
                         │    SQLite (dev) or    │
                         │    PostgreSQL (prod)  │
                         └───────────────────────┘
```

For production, replace the self-signed TLS termination with a managed certificate and use PostgreSQL instead of SQLite.