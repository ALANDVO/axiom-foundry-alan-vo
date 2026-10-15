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