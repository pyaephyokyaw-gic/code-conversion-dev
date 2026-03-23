from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, ForeignKey, func, Enum as SQLEnum
from datetime import datetime
from .base import Base
from common.user_role import UserRole


class User(Base):
    __tablename__ = "users"
    # primary_key=True makes this the unique ID for each user
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"))
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"))
    name: Mapped[str] = mapped_column(
        String(50), nullable=False)
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False)
    cognito_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    role: Mapped[int] = mapped_column(
        SQLEnum(UserRole, name="user_role"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
