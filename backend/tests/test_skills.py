import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio

from app.main import app
from app.core.database import get_db, Base
from app.models.skill import Skill
from app.services.skill_search import build_skill_search_query

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
_transport = ASGITransport(app=app)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Seed data
    skills = [
        Skill(
            name="tdd-workflow",
            description="Test-driven development workflow",
            category="workflow",
            platform="claude",
            capability="tdd",
            tags=["testing", "workflow"],
            config={"hooks": ["pre-commit"]},
            version="1.0.0",
            author="ECC",
        ),
        Skill(
            name="security-review",
            description="Security code review skill",
            category="security",
            platform="claude",
            capability="security",
            tags=["security", "review"],
            config={},
            version="1.0.0",
            author="ECC",
        ),
        Skill(
            name="frontend-dev",
            description="Frontend development skill",
            category="development",
            platform="cursor",
            capability="frontend",
            tags=["react", "typescript"],
            config={"extensions": ["eslint"]},
            version="1.0.0",
            author="Community",
        ),
    ]
    db.add_all(skills)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.get("/api/skills/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_list_skills():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.get("/api/skills")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["page"] == 1
        assert data["page_size"] == 20


@pytest.mark.asyncio
async def test_list_skills_with_search():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.get("/api/skills?search=tdd")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "tdd-workflow"


@pytest.mark.asyncio
async def test_list_skills_with_category_filter():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.get("/api/skills?category=security")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category"] == "security"


@pytest.mark.asyncio
async def test_list_skills_with_platform_filter():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.get("/api/skills?platform=cursor")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["platform"] == "cursor"


@pytest.mark.asyncio
async def test_get_skill():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.get("/api/skills/1")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "tdd-workflow"
        assert data["capability"] == "tdd"


@pytest.mark.asyncio
async def test_get_skill_not_found():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.get("/api/skills/999")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_skill_by_name():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.get("/api/skills/name/security-review")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "security-review"


@pytest.mark.asyncio
async def test_create_skill():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.post(
            "/api/skills",
            json={
                "name": "new-skill",
                "description": "A new skill",
                "category": "testing",
                "platform": "claude",
                "capability": "tdd",
                "tags": ["new"],
                "config": {},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "new-skill"
        assert data["id"] == 4


@pytest.mark.asyncio
async def test_create_skill_duplicate():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.post(
            "/api/skills",
            json={
                "name": "tdd-workflow",
                "description": "Duplicate",
                "category": "workflow",
                "platform": "claude",
            },
        )
        assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_skill_missing_fields():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.post(
            "/api/skills",
            json={"name": "incomplete"},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_skill():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.patch(
            "/api/skills/1",
            json={"description": "Updated description", "version": "2.0.0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["version"] == "2.0.0"


@pytest.mark.asyncio
async def test_delete_skill():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.delete("/api/skills/1")
        assert response.status_code == 204

        response = await client.get("/api/skills/1")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_pagination():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.get("/api/skills?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 3
        assert data["total_pages"] == 2


@pytest.mark.asyncio
async def test_sorting():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.get("/api/skills?sort=name&order=desc")
        assert response.status_code == 200
        data = response.json()
        names = [item["name"] for item in data["items"]]
        assert names == sorted(names, reverse=True)


@pytest.mark.asyncio
async def test_meta_endpoints():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        cats = await client.get("/api/skills/meta/categories")
        assert cats.status_code == 200
        assert "workflow" in cats.json()
        assert "security" in cats.json()

        platforms = await client.get("/api/skills/meta/platforms")
        assert platforms.status_code == 200
        assert "claude" in platforms.json()
        assert "cursor" in platforms.json()

        caps = await client.get("/api/skills/meta/capabilities")
        assert caps.status_code == 200
        assert "tdd" in caps.json()
        assert "security" in caps.json()


@pytest.mark.asyncio
async def test_real_http_create_and_read():
    """Integration test crossing the real HTTP boundary (uvicorn + httpx)."""
    import uvicorn

    config = uvicorn.Config(app, host="127.0.0.1", port=8123)
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    try:
        await asyncio.sleep(0.5)
        async with AsyncClient(base_url="http://127.0.0.1:8123") as client:
            response = await client.post(
                "/api/skills",
                json={
                    "name": "http-integration-skill",
                    "description": "Created via real HTTP",
                    "category": "integration",
                    "platform": "claude",
                    "tags": ["http"],
                },
            )
            assert response.status_code == 201
            created = response.json()
            assert created["name"] == "http-integration-skill"

            response = await client.get(f"/api/skills/{created['id']}")
            assert response.status_code == 200
            fetched = response.json()
            assert fetched["name"] == "http-integration-skill"
            assert fetched["description"] == "Created via real HTTP"
    finally:
        server.should_exit = True
        await asyncio.wait_for(task, timeout=5)


def test_build_skill_search_query_search(db_session):
    query = db_session.query(Skill)
    query = build_skill_search_query(query, search="tdd")
    results = query.all()
    assert len(results) == 1
    assert results[0].name == "tdd-workflow"


def test_build_skill_search_query_combined_filters(db_session):
    query = db_session.query(Skill)
    query = build_skill_search_query(
        query,
        search=None,
        category="security",
        platform="claude",
        capability="security",
    )
    results = query.all()
    assert len(results) == 1
    assert results[0].name == "security-review"


def test_build_skill_search_query_empty_search(db_session):
    query = db_session.query(Skill)
    query = build_skill_search_query(query, search="")
    results = query.all()
    assert len(results) == 3

# Platform config generation endpoint tests
@pytest.mark.asyncio
async def test_get_supported_platform_configs():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.get("/api/skills/meta/platform-config/platforms")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "claude" in data
        assert "cursor" in data
        assert "opencode" in data
        assert "codex" in data
        assert "gemini" in data
        assert "zed" in data


@pytest.mark.asyncio
async def test_get_skill_platform_config():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        # First create a skill with config
        skill_data = {
            "name": "platform-test-skill",
            "description": "Test skill for platform config",
            "category": "testing",
            "platform": "claude",
            "config": {
                "command": "python",
                "args": ["-m", "pytest"],
                "env": {"TEST": "true"},
                "cwd": "/project",
                "timeout": 300,
            },
        }
        create_response = await client.post("/api/skills", json=skill_data)
        assert create_response.status_code == 201
        skill_id = create_response.json()["id"]

        # Get platform config for claude
        response = await client.get(f"/api/skills/{skill_id}/platform-config/claude")
        assert response.status_code == 200
        config = response.json()
        assert config["command"] == "python"
        assert config["args"] == ["-m", "pytest"]
        assert config["env"] == {"TEST": "true"}
        assert config["cwd"] == "/project"
        assert config["timeout"] == 300


@pytest.mark.asyncio
async def test_get_skill_platform_config_by_name():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        skill_data = {
            "name": "platform-test-by-name",
            "description": "Test skill for platform config by name",
            "category": "testing",
            "platform": "cursor",
            "config": {
                "command": "node",
                "args": ["script.js"],
                "hotkey": "cmd+shift+t",
            },
        }
        create_response = await client.post("/api/skills", json=skill_data)
        assert create_response.status_code == 201

        response = await client.get("/api/skills/name/platform-test-by-name/platform-config/cursor")
        assert response.status_code == 200
        config = response.json()
        assert config["command"] == "node"
        assert config["hotkey"] == "cmd+shift+t"


@pytest.mark.asyncio
async def test_get_skill_platform_config_not_found():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        response = await client.get("/api/skills/999/platform-config/claude")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_skill_platform_config_invalid_platform():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        skill_data = {
            "name": "invalid-platform-test",
            "description": "Test",
            "category": "testing",
            "platform": "claude",
            "config": {},
        }
        create_response = await client.post("/api/skills", json=skill_data)
        assert create_response.status_code == 201
        skill_id = create_response.json()["id"]

        response = await client.get(f"/api/skills/{skill_id}/platform-config/unknown-platform")
        assert response.status_code == 400
        assert "Unsupported platform" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_skill_platform_config_codex():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        skill_data = {
            "name": "codex-config-test",
            "description": "Test Codex config",
            "category": "testing",
            "platform": "codex",
            "config": {
                "prompt": "Review this code",
                "model": "gpt-4",
                "temperature": 0.5,
                "max_tokens": 2000,
            },
        }
        create_response = await client.post("/api/skills", json=skill_data)
        assert create_response.status_code == 201
        skill_id = create_response.json()["id"]

        response = await client.get(f"/api/skills/{skill_id}/platform-config/codex")
        assert response.status_code == 200
        config = response.json()
        assert config["prompt"] == "Review this code"
        assert config["model"] == "gpt-4"
        assert config["temperature"] == 0.5
        assert config["max_tokens"] == 2000


@pytest.mark.asyncio
async def test_get_skill_platform_config_gemini():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        skill_data = {
            "name": "gemini-config-test",
            "description": "Test Gemini config",
            "category": "testing",
            "platform": "gemini",
            "config": {
                "prompt": "Explain this",
                "model": "gemini-1.5-flash",
                "temperature": 0.3,
            },
        }
        create_response = await client.post("/api/skills", json=skill_data)
        assert create_response.status_code == 201
        skill_id = create_response.json()["id"]

        response = await client.get(f"/api/skills/{skill_id}/platform-config/gemini")
        assert response.status_code == 200
        config = response.json()
        assert config["prompt"] == "Explain this"
        assert config["model"] == "gemini-1.5-flash"
        assert config["temperature"] == 0.3
        assert config["max_output_tokens"] == 4000  # default


@pytest.mark.asyncio
async def test_get_skill_platform_config_case_insensitive():
    async with AsyncClient(transport=_transport, base_url="http://test") as client:
        skill_data = {
            "name": "case-test",
            "description": "Test case insensitivity",
            "category": "testing",
            "platform": "claude",
            "config": {"command": "test"},
        }
        create_response = await client.post("/api/skills", json=skill_data)
        assert create_response.status_code == 201
        skill_id = create_response.json()["id"]

        response = await client.get(f"/api/skills/{skill_id}/platform-config/CLAUDE")
        assert response.status_code == 200
        assert response.json()["command"] == "test"

        response = await client.get(f"/api/skills/{skill_id}/platform-config/Claude-Code")
        assert response.status_code == 200
        assert response.json()["command"] == "test"

