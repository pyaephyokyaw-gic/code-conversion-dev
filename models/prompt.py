from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, func, DateTime, ForeignKey
from datetime import datetime
from .base import Base


class Prompt(Base):
    __tablename__ = "prompts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    prompt_name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False)
    prompt_description: Mapped[str] = mapped_column(String(255))
    prompt_file_url: Mapped[str] = mapped_column()
    input_file_type: Mapped[str] = mapped_column()
    output_file_type: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
