from ..repositories.conversion_repository import ConversionRepository
from datetime import datetime
import json
import os
import boto3


class ConversionService:
    @staticmethod
    def get_conversion_service(limit: int, user_id, is_admin):
        conversions = ConversionRepository.get_conversions_from_db(
            limit, user_id, is_admin)
        result = []
        for row in conversions:
            row_dict = row._asdict()
            if row_dict.get("completed_at"):
                row_dict["processingTime"] = round((
                    row_dict["completed_at"] - row_dict['created_at']).total_seconds(), 3)
            else:
                row_dict["processingTime"] = None

            row_dict["date"] = row_dict["created_at"].isoformat()
            result.append(row_dict)

        return result

    @staticmethod
    def create_conversion(user_id, prompt_id, input_file_url):
        data = {
            "user_id": user_id,
            "prompt_id": prompt_id,
            "input_file": input_file_url,
            "status": "processing",
            "created_at": datetime.now()
        }

        return ConversionRepository.insert_conversion(data)

    @staticmethod
    def complete_conversion_success(user_id, convresion_id, output_file_url, usage_token, usage_credit):
        data = {
            "status": "completed",
            "output_file": output_file_url,
            "completed_at": datetime.now()
        }

        usage_data = {
            "user_id": user_id,
            "conversion_id": convresion_id,
            "total_tokens": usage_token,
            "total_credits": usage_credit,
        }
        return ConversionRepository.update_conversion(convresion_id, data, usage_data)

    @staticmethod
    def complete_conversion_fail(user_id, convresion_id, error_message, usage_token, usage_credit):
        data = {
            "status": "failed",
            "fail_log": error_message,
            "completed_at": datetime.now()
        }

        usage_data = {
            "user_id": user_id,
            "conversion_id": convresion_id,
            "total_tokens": usage_token,
            "total_credits": usage_credit,
        }
        return ConversionRepository.update_conversion(convresion_id, data, usage_data)

    @staticmethod
    def enqueue_conversion_job(conversion_id, user_id, prompt_id, input_file_url):
        queue_url = os.environ.get("CONVERSION_QUEUE_URL")
        if not queue_url:
            return False

        payload = {
            "conversion_id": conversion_id,
            "user_id": user_id,
            "prompt_id": prompt_id,
            "input_file_url": input_file_url,
        }
        sqs = boto3.client("sqs")
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(payload),
        )
        return True
