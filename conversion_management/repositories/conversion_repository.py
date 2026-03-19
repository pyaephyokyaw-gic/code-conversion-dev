from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.organization import Org
from models.conversion import Conversion
from models.user import User
from models.prompt import Prompt
from models.company import Company
from models.usage_logs import UsageLog
from fastapi import HTTPException


async def fetch_conversion_logs(db: AsyncSession, user_id: str, is_admin: bool, limit: int, offset: int):
    stmt = (
        select(
            Conversion.id.label("conversion_id"),
            Conversion.created_at.label("processing_date"),
            Conversion.status,
            Conversion.fail_log,
            Conversion.completed_at,
            Conversion.input_file.label("s3_input_url"),
            Conversion.output_file.label("s3_output_url"),

            User.id.label("user_id"),
            User.email.label("user_email"),

            Org.id.label("organization_id"),
            Org.name.label("organization_name"),

            Company.id.label("company_id"),
            Company.name.label("company_name"),

            Prompt.prompt_name.label("prompt_name"),

            UsageLog.total_tokens.label("token_usage"),
            UsageLog.total_credits.label("credit_usage"),
        )
        .select_from(Conversion)

        # INNER JOINs (required relationships)
        .join(User, User.id == Conversion.user_id)
        .join(Org, Org.id == User.organization_id)
        .join(Company, Company.id == User.company_id)
        .join(Prompt, Prompt.id == Conversion.prompt_id)
        .join(UsageLog, UsageLog.conversion_id == Conversion.id)
        # ORDER + Pagination
        .order_by(Conversion.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    # ✅ KEEP THIS CONDITION (as requested)
    if not is_admin:
        stmt = stmt.where(Conversion.user_id == user_id)

    result = await db.execute(stmt)
    data = result.fetchall()
    if not data:
        raise HTTPException(status_code=200, detail="No data found")

    return data
