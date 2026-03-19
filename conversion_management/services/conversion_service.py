import json
from ..repositories.conversion_repository import fetch_conversion_logs
from ..models.conversion_models import Conversion, ConversionLog
from common.user_role import UserRole


async def get_conversion_results_service(limit, offset, user, db):
    is_admin = user.role == UserRole.SYSTEM_ADMIN
    rows = await fetch_conversion_logs(db=db, user_id=user.id, is_admin=is_admin, limit=limit, offset=offset)
    if is_admin:
        return [
            ConversionLog(
                id=row.conversion_id,
                promptType=row.prompt_name,
                date=row.processing_date,
                status=row.status,
                failLog=row.fail_log,
                s3Input=row.s3_input_url,
                userId=row.user_id,
                user=row.user_email,
                organizationId=row.organization_id,
                organizationName=row.organization_name,
                companyId=row.company_id,
                companyName=row.company_name,
                creditUsage=row.credit_usage,
            ) for row in rows
        ]
    else:
        return [
            Conversion(
                id=row.conversion_id,
                promptType=row.prompt_name,
                date=row.processing_date,
                status=row.status,
                s3Input=row.s3_input_url,
                tokenUsage=row.token_usage,
                s3Output=row.s3_output_url,
                processingTime=row.completed_at
            ) for row in rows
        ]
