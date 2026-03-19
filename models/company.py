from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey
from datetime import datetime
from .base import Base


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column()
    domain: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=datetime.now(), onupdate=datetime.now())
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
