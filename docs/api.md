# API Reference

## Health

`GET /api/skills/health`

Returns service health status.

**Response** `200 OK`:
```json
{"status": "ok", "service": "axiom-foundry"}
```

## List Skills

`GET /api/skills`

Returns a paginated, filtered, and sorted list of skills.

### Query Parameters

| Parameter   | Type | Required | Default | Constraints |
|-------------|------|----------|---------|-------------|
| `page`      | int  | no       | 1       | ≥ 1         |
| `page_size` | int  | no       | 20      | 1–100       |
| `search`    | str  | no       | —       | —           |
| `category`  | str  | no       | —       | —           |
| `platform`  | str  | no       | —       | —           |
| `capability`| str  | no       | —       | —           |
| `sort`      | str  | no       | name    | Skill column name |
| `order`     | str  | no       | asc     | `asc` or `desc` |

### Response `200 OK`

```json
{
  "items": [
    {
      "id": 1,
      "name": "tdd-workflow",
      "description": "Test-driven development workflow",
      "category": "workflow",
      "platform": "claude",
      "capability": "tdd",
      "tags": ["testing", "workflow"],
      "config": {"hooks": ["pre-commit"]},
      "version": "1.0.0",
      "author": "ECC",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

## Get Skill by ID

`GET /api/skills/{skill_id}`

Returns a single skill.

**Response** `200 OK`: Skill object.
**Error** `404 Not Found`: Skill not found.

## Get Skill by Name

`GET /api/skills/name/{name}`

Returns a single skill by its unique name.

**Response** `200 OK`: Skill object.
**Error** `404 Not Found`: Skill not found.

## Create Skill

`POST /api/skills`

Creates a new skill.

**Request Body**:
```json
{
  "name": "my-skill",
  "description": "Description",
  "category": "workflow",
  "platform": "claude",
  "capability": "tdd",
  "tags": ["tag1"],
  "config": {},
  "version": "1.0.0",
  "author": "Author"
}
```

**Response** `201 Created`: Created skill object.
**Error** `409 Conflict`: Skill with this name already exists.
**Error** `422 Unprocessable Entity`: Validation error.

## Update Skill

`PATCH /api/skills/{skill_id}`

Updates one or more fields of a skill. Only provided fields are updated.

**Response** `200 OK`: Updated skill object.
**Error** `404 Not Found`: Skill not found.

## Delete Skill

`DELETE /api/skills/{skill_id}`

Deletes a skill.

**Response** `204 No Content`: Skill deleted.
**Error** `404 Not Found`: Skill not found.

## Metadata Endpoints

### List Categories

`GET /api/skills/meta/categories`

**Response** `200 OK`: `["workflow", "security", "development"]`

### List Platforms

`GET /api/skills/meta/platforms`

**Response** `200 OK`: `["claude", "cursor"]`

### List Capabilities

`GET /api/skills/meta/capabilities`

**Response** `200 OK`: `["tdd", "security", "frontend"]`

## Skill Object

| Field         | Type           | Description |
|---------------|----------------|-------------|
| `id`          | int            | Unique identifier |
| `name`        | str            | Skill name (unique) |
| `description` | str            | Detailed description |
| `category`    | str            | Category (e.g., workflow, security) |
| `platform`    | str            | Target platform |
| `capability`  | str or null    | Capability type |
| `tags`        | list[str]      | Searchable tags |
| `config`      | dict           | Platform-specific configuration |
| `version`     | str            | Skill version |
| `author`      | str or null    | Author name |
| `created_at`  | str (ISO 8601) | Creation timestamp (UTC) |
| `updated_at`  | str (ISO 8601) | Last modification timestamp (UTC) |