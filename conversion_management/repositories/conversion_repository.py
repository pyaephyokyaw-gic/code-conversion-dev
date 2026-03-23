from sqlalchemy import select
from models.organization import Org
from models.conversion import Conversion
from models.user import User
from models.prompt import Prompt
from models.company import Company
from models.usage_logs import UsageLog
from db.database import SessionLocal


class ConversionRepository:
    @staticmethod
    def get_conversions_from_db(limit, user_id, is_admin):
        db = SessionLocal()
        try:
            stmt = (
                select(
                    Conversion.id.label("id"),
                    Conversion.created_at.label("created_at"),
                    Conversion.status.label("status"),
                    Conversion.fail_log.label("failLog"),
                    Conversion.completed_at.label("completed_at"),
                    Conversion.input_file.label("s3Input"),
                    Conversion.output_file.label("s3Output"),

                    User.id.label("userId"),
                    User.email.label("user"),

                    Org.id.label("organizationId"),
                    Org.name.label("organizationName"),

                    Company.id.label("companyId"),
                    Company.name.label("companyName"),

                    Prompt.prompt_name.label("promptType"),

                    UsageLog.total_tokens.label("tokenUsage"),
                    UsageLog.total_credits.label("creditUsage"),
                )
                .select_from(Conversion)
                .join(User, User.id == Conversion.user_id)
                .join(Org, Org.id == User.organization_id)
                .join(Company, Company.id == User.company_id)
                .join(Prompt, Prompt.id == Conversion.prompt_id)
                .join(UsageLog, UsageLog.conversion_id == Conversion.id)
                .order_by(Conversion.created_at.desc())
                .limit(limit)
            )
            if not is_admin:
                stmt = stmt.where(Conversion.user_id == user_id)

            result = db.execute(stmt)
            return result.fetchall()
        finally:
            db.close()

    @staticmethod
    def insert_conversion(data):
        db = SessionLocal()
        try:
            conversion = Conversion(**data)
            db.add(conversion)
            db.commit()
            db.refresh(conversion)
            return {
                "conversion_id": conversion.id,
                "message": "success"
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def update_conversion(conversion_id, data, usage_data):
        db = SessionLocal()
        try:
            conversion = db.query(Conversion).filter(
                Conversion.id == conversion_id).first()

            if not conversion:
                return None
            for key, value in data.items():
                setattr(conversion, key, value)

            # insert for usage log
            usage_log = UsageLog(**usage_data)
            db.add(usage_log)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def get_user_by_cognito_id(cognito_id):
        db = SessionLocal()
        try:
            stmt = select(User).where(User.cognito_id == cognito_id)
            result = db.execute(stmt)
            return result.scalar_one_or_none()
        finally:
            db.close()
