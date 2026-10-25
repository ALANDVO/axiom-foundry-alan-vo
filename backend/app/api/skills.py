from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.core.database import get_db
from app.models.skill import Skill
from app.services.skill_search import build_skill_search_query
from app.services.platform_config import generate_platform_config, get_supported_platforms

router = APIRouter(prefix="/api/skills", tags=["skills"])


class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1, max_length=100)
    platform: str = Field(..., min_length=1, max_length=50)
    capability: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(default_factory=list)
    config: Optional[dict] = Field(default_factory=dict)
    version: str = Field("1.0.0", max_length=50)
    author: Optional[str] = Field(None, max_length=255)


class SkillUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    platform: Optional[str] = Field(None, min_length=1, max_length=50)
    capability: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    config: Optional[dict] = None
    version: Optional[str] = Field(None, max_length=50)
    author: Optional[str] = Field(None, max_length=255)


class SkillResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    platform: str
    capability: Optional[str]
    tags: List[str]
    config: dict
    version: str
    author: Optional[str]
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class SkillListResponse(BaseModel):
    items: List[SkillResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("/health")
def health():
    return {"status": "ok", "service": "axiom-foundry"}


@router.get("", response_model=SkillListResponse)
def list_skills(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    capability: Optional[str] = Query(None),
    sort: str = Query("name"),
    order: str = Query("asc"),
):
    query = db.query(Skill)

    query = build_skill_search_query(query, search, category, platform, capability)

    sort_column = getattr(Skill, sort, Skill.name)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return SkillListResponse(
        items=[SkillResponse.model_validate(item.to_dict()) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillResponse.model_validate(skill.to_dict())


@router.get("/name/{name}", response_model=SkillResponse)
def get_skill_by_name(name: str, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.name == name).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillResponse.model_validate(skill.to_dict())


@router.post("", response_model=SkillResponse, status_code=201)
def create_skill(skill: SkillCreate, db: Session = Depends(get_db)):
    existing = db.query(Skill).filter(Skill.name == skill.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Skill with this name already exists")

    db_skill = Skill(**skill.model_dump())
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return SkillResponse.model_validate(db_skill.to_dict())


@router.patch("/{skill_id}", response_model=SkillResponse)
def update_skill(skill_id: int, skill: SkillUpdate, db: Session = Depends(get_db)):
    db_skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    update_data = skill.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_skill, field, value)

    db.commit()
    db.refresh(db_skill)
    return SkillResponse.model_validate(db_skill.to_dict())


@router.delete("/{skill_id}", status_code=204)
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    db_skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(db_skill)
    db.commit()
    return None


@router.get("/meta/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db)):
    return [row[0] for row in db.query(Skill.category).distinct().all()]


@router.get("/meta/platforms", response_model=List[str])
def get_platforms(db: Session = Depends(get_db)):
    return [row[0] for row in db.query(Skill.platform).distinct().all()]


@router.get("/meta/capabilities", response_model=List[str])
def get_capabilities(db: Session = Depends(get_db)):
    return [row[0] for row in db.query(Skill.capability).distinct().all() if row[0]]


@router.get("/meta/platform-config/platforms", response_model=List[str])
def get_supported_platform_configs():
    """List all supported platform configuration formats."""
    return get_supported_platforms()


@router.get("/{skill_id}/platform-config/{platform}")
def get_skill_platform_config(skill_id: int, platform: str, db: Session = Depends(get_db)):
    """Generate platform-specific configuration for a skill.

    Returns the configuration formatted for the target platform (Claude Code, Cursor, OpenCode, etc.).
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    try:
        platform_config = generate_platform_config(platform, skill.config or {})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content=platform_config)


@router.get("/name/{name}/platform-config/{platform}")
def get_skill_platform_config_by_name(name: str, platform: str, db: Session = Depends(get_db)):
    """Generate platform-specific configuration for a skill by name."""
    skill = db.query(Skill).filter(Skill.name == name).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    try:
        platform_config = generate_platform_config(platform, skill.config or {})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content=platform_config)

