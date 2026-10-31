from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Run(Base):
    __tablename__ = "runs"

    id = Column(String(36), primary_key=True)
    status = Column(String(16), nullable=False, default="queued", index=True)
    source = Column(String(16), nullable=False, default="upload")
    as_of = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error = Column(Text, nullable=True)
    files_json = Column(Text, nullable=False, default="{}")
    summary_json = Column(Text, nullable=True)
    report_dir = Column(Text, nullable=False)
