from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.core.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)  # claude, codex, cursor, opencode, gemini, zed, etc.
    capability = Column(String(100), nullable=True, index=True)  # tdd, security, docs, frontend, data, ml, ops
    tags = Column(JSON, nullable=True)  # list of strings
    config = Column(JSON, nullable=True)  # platform-specific config
    version = Column(String(50), nullable=False, default="1.0.0")
    author = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_skills_category_platform", "category", "platform"),
        Index("ix_skills_name_desc", "name", "description"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "platform": self.platform,
            "capability": self.capability,
            "tags": self.tags or [],
            "config": self.config or {},
            "version": self.version,
            "author": self.author,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }