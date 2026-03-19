from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime
from datetime import datetime
from .base import Base


class Org(Base):
    __tablename__ = "organizations"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=datetime.now(), onupdate=datetime.now())
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
