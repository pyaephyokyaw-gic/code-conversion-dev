from .controllers.conversion_controller import ConversionController
from .services.conversion_service import ConversionService
import json


def lambda_handler(event, context):
    try:
        if _is_sqs_event(event):
            return _handle_sqs_event(event)

        return _handle_http_event(event)

    except Exception as e:
        print(f"[ERROR] Unhandled exception: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }

# ------------------------
# Event Type Detection
# ------------------------


def _is_sqs_event(event):
    records = event.get("Records")
    return (
        isinstance(records, list)
        and len(records) > 0
        and records[0].get("eventSource") == "aws:sqs"
    )

# ------------------------
# HTTP Handling
# ------------------------


def _handle_http_event(event):
    path = event.get("path") or event.get("rawPath")
    method = (
        event.get("httpMethod")
        or event.get("requestContext", {}).get("http", {}).get("method")
        or ""
    ).upper()

    routes = {
        ("GET", "/conversions"): ConversionController.get_conversions,
        ("POST", "/conversion"): ConversionController.insert_conversion,
    }

    handler = routes.get((method, path))

    if not handler:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Not Found"}),
        }

    return handler(event)

# ------------------------
# SQS Handling
# ------------------------


def _handle_sqs_event(event):
    failed = []

    for record in event.get("Records", []):
        message_id = record.get("messageId")

        try:
            body = json.loads(record.get("body", "{}"))

            conversion_id = body["conversion_id"]
            user_id = body["user_id"]
            input_file_url = body.get("input_file_url")

            # Simulated processing
            output_file_url = (
                f"{input_file_url}.converted" if input_file_url else None
            )

            ConversionService.complete_conversion_success(
                user_id=user_id,
                conversion_id=conversion_id,  # ✅ fixed typo
                output_file_url=output_file_url,
                usage_token=300,
                usage_credit=1,
            )

        except Exception as e:
            print(f"[ERROR] SQS processing failed: {str(e)}")

            try:
                if "conversion_id" in body and "user_id" in body:
                    ConversionService.complete_conversion_fail(
                        user_id=body["user_id"],
                        conversion_id=body["conversion_id"],
                        error_message=str(e),
                        usage_token=0,
                        usage_credit=0,
                    )
            finally:
                if message_id:
                    failed.append({"itemIdentifier": message_id})

    return {"batchItemFailures": failed}
