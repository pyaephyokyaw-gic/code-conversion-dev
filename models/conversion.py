from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, ForeignKey, DateTime, func, Enum as SQLEnum
from .base import Base
from datetime import datetime
from enum import Enum


class ConversionStatus(str, Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'


class Conversion(Base):
    __tablename__ = "conversions"
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    prompt_id: Mapped[int] = mapped_column(
        ForeignKey("prompts.id"), index=True)
    input_file: Mapped[str] = mapped_column(String)
    output_file: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[int] = mapped_column(
        SQLEnum(ConversionStatus, name="conversion_status_enum"))
    fail_log: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now())
    completed_at: Mapped[datetime] = mapped_column(DateTime)
