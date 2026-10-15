from typing import Optional

from sqlalchemy import or_, String
from sqlalchemy.orm import Query

from app.models.skill import Skill


def build_skill_search_query(
    query: Query,
    search: Optional[str] = None,
    category: Optional[str] = None,
    platform: Optional[str] = None,
    capability: Optional[str] = None,
) -> Query:
    """Apply search and filter conditions to a Skill query.

    Encapsulates the deterministic search/filter logic so route handlers
    stay thin and the algorithm is independently testable.
    """
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Skill.name.ilike(term),
                Skill.description.ilike(term),
                Skill.tags.cast(String).ilike(term),
            )
        )

    if category:
        query = query.filter(Skill.category == category)
    if platform:
        query = query.filter(Skill.platform == platform)
    if capability:
        query = query.filter(Skill.capability == capability)

    return query