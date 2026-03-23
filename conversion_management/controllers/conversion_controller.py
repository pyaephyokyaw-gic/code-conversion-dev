import json
from fastapi import HTTPException
from ..services.conversion_service import ConversionService
from dependencies.get_current_user import get_current_user
from common.user_role import UserRole
from ..models.conversion_models import Conversion, ConversionLog


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
    }


class ConversionController:
    @staticmethod
    def get_conversions(event):
        try:
            user = get_current_user(event)
            is_admin = user.role == UserRole.SYSTEM_ADMIN
            query = event.get("queryStringParameters") or {}
            raw_limit = query.get("limit", 10)
            try:
                limit = int(raw_limit)
            except (TypeError, ValueError):
                return _response(400, {"error": "Invalid limit. limit must be an integer."})

            if limit < 1 or limit > 100:
                return _response(400, {"error": "Invalid limit. Supported range is 1-100."})

            conversions = ConversionService.get_conversion_service(
                limit, user_id=user.id, is_admin=is_admin)

            if not conversions:
                return _response(200, [])

            if is_admin:
                result = [ConversionLog(**row).model_dump()
                          for row in conversions]
            else:
                result = [Conversion(**row).model_dump()
                          for row in conversions]

            return _response(200, result)
        except HTTPException as e:
            return _response(e.status_code, {"error": e.detail})
        except Exception as e:
            return _response(500, {"error": str(e)})

    @staticmethod
    def insert_conversion(event):
        try:
            user = get_current_user(event)
            body = json.loads(event.get("body", "{}"))
            user_id = user.id
            prompt_id = body.get("prompt_id")
            input_file_url = body.get("s3InputFileUrl")

            conversion = ConversionService.create_conversion(
                user_id=user_id,
                prompt_id=prompt_id,
                input_file_url=input_file_url
            )
            conversion_id = conversion["conversion_id"]
            print("conversion id", conversion_id)
            # Async-ready: persist request then enqueue processing job.
            # This keeps current response shape while decoupling heavy AI work from request latency.
            queued = ConversionService.enqueue_conversion_job(
                conversion_id=conversion_id,
                user_id=user_id,
                prompt_id=prompt_id,
                input_file_url=input_file_url,
            )

            if not queued:
                ConversionService.complete_conversion_fail(
                    user_id,
                    conversion_id,
                    "Failed to enqueue conversion request",
                    usage_token=0,
                    usage_credit=0,
                )
                return _response(500, {"status": "failed", "conversion_id": conversion_id})

            return _response(200, {"status": "success", "conversion_id": conversion_id})

        except Exception as e:
            return _response(500, {"error": str(e)})
