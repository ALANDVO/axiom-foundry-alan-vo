# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-25

### Added
- Platform config generator service supporting 7 AI coding agent platforms:
  - Claude Code / Claude
  - Cursor
  - OpenCode
  - Codex
  - Gemini
  - Zed
- New API endpoints:
  - `GET /api/skills/meta/platform-config/platforms` - List supported platform config formats
  - `GET /api/skills/{id}/platform-config/{platform}` - Generate platform config by skill ID
  - `GET /api/skills/name/{name}/platform-config/{platform}` - Generate platform config by skill name
- Frontend platform config modal with:
  - Platform-specific configuration preview
  - Copy to clipboard functionality
  - Download JSON file functionality
- Comprehensive test coverage:
  - 18 unit tests for platform config generators
  - 10 integration tests for new API endpoints

### Changed
- Updated feature-plan.json to track platform-adapters feature as in_progress
- Updated PLAN.md with current feature status

### Fixed
- None

## [0.1.0] - 2026-10-15

### Added
- FastAPI backend with skill registry API
- React/TypeScript frontend with skill browsing
- SQLite persistence with SQLAlchemy
- Full-text search, filtering, pagination, sorting
- Docker Compose for local development
- Keycloak realm configuration for OIDC/SAML
- pytest and vitest test suites

### Changed
- N/A (initial release)

### Fixed
- N/A
