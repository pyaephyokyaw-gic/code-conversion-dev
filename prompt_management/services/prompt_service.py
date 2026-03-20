"""
Prompt Service
Contains business logic for prompt operations
"""
import os
import boto3
from repositories.prompt_repository import (
    create_prompt as repo_create,
    get_prompt_by_id as repo_get_by_id,
    get_basic_prompt_by_id,
    update_prompt as repo_update,
    delete_prompt as repo_delete,
    update_file_url,
    list_prompts_grouped
)

S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
AWS_REGION = os.environ.get("AWS_REGION_NAME", "ap-northeast-1")
s3 = boto3.client("s3", region_name=AWS_REGION)


def _s3_url(key):
    """Generate S3 URL."""
    return f"s3://{S3_BUCKET}/{key}"


def _make_key(org_id, filename):
    """Create S3 key from organization ID and filename."""
    return filename


def _upload_to_s3(key, content):
    """Upload content to S3."""
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=content.encode("utf-8"),
        ContentType="text/plain",
    )


def _delete_from_s3(file_url):
    """Delete file from S3."""
    if file_url:
        key = file_url.split(f"s3://{S3_BUCKET}/")[1]
        s3.delete_object(Bucket=S3_BUCKET, Key=key)


def _presigned_put(key, expires=3600):
    """Generate presigned URL for upload."""
    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=expires,
    )


def create_prompt(body):
    """Create a new prompt with optional S3 file upload."""
    org_id = body.get("organization_id")
    company_id = body.get("company_id")

    if not org_id:
        return None, "organization_id is required"
    if not company_id:
        return None, "company_id is required"

    name = body.get("prompt_name")
    description = body.get("prompt_description")
    input_file_type = body.get("input_file_type")
    output_file_type = body.get("output_file_type")
    filename = body.get("file_name")
    content = body.get("prompt_content")

    file_url = None
    if filename and content:
        key = _make_key(org_id, filename)
        try:
            _upload_to_s3(key, content)
            file_url = _s3_url(key)
        except Exception as e:
            return None, f"S3 upload failed: {str(e)}"
    elif filename and not content:
        key = _make_key(org_id, filename)
        file_url = _s3_url(key)

    try:
        prompt = repo_create(
            org_id, company_id, name, description,
            input_file_type, output_file_type, file_url
        )
        return {"prompt": prompt}, None
    except Exception as e:
        return None, str(e)


def get_prompt_by_id(prompt_id):
    """Get a prompt by ID with organization and company details."""
    try:
        prompt = repo_get_by_id(prompt_id)
        if not prompt:
            return None, f"Prompt {prompt_id} not found"
        return {"prompt": prompt}, None
    except Exception as e:
        return None, str(e)


def list_prompts(query_params):
    """List prompts with filtering and pagination."""
    qp = query_params or {}
    org_id = qp.get("organization_id")
    company_id = qp.get("company_id")
    search = qp.get("search")
    page = max(int(qp.get("page", 1)), 1)
    limit = max(int(qp.get("limit", 5)), 1)

    try:
        result = list_prompts_grouped(org_id, company_id, search, page, limit)
        return result, None
    except Exception as e:
        return None, str(e)


def update_prompt(prompt_id, body):
    """Update all fields of a prompt with optional S3 file replacement."""
    org_id = body.get("organization_id")
    company_id = body.get("company_id")
    name = body.get("prompt_name")
    description = body.get("prompt_description")
    input_file_type = body.get("input_file_type")
    output_file_type = body.get("output_file_type")
    filename = body.get("file_name")
    content = body.get("prompt_content")

    try:
        existing = get_basic_prompt_by_id(prompt_id)
        if not existing:
            return None, f"Prompt {prompt_id} not found"

        old_file_url = existing.get("prompt_file_url")
        file_url = None

        # Use new org_id if provided, else use existing
        use_org_id = org_id if org_id else existing["organization_id"]

        if filename and content:
            key = _make_key(use_org_id, filename)
            if old_file_url:
                try:
                    _delete_from_s3(old_file_url)
                except Exception as e:
                    return None, f"S3 delete old file failed: {str(e)}"
            try:
                _upload_to_s3(key, content)
                file_url = _s3_url(key)
            except Exception as e:
                return None, f"S3 upload failed: {str(e)}"
        elif filename and not content:
            key = _make_key(use_org_id, filename)
            file_url = _s3_url(key)

        updated = repo_update(
            prompt_id, org_id, company_id, name, description, 
            input_file_type, output_file_type, file_url
        )
        return {"prompt": updated}, None
    except Exception as e:
        return None, str(e)


def delete_prompt(prompt_id):
    """Delete a prompt and its S3 file."""
    try:
        existing = get_basic_prompt_by_id(prompt_id)
        if not existing:
            return None, f"Prompt {prompt_id} not found"

        file_url = existing.get("prompt_file_url")
        if file_url:
            try:
                _delete_from_s3(file_url)
            except Exception as e:
                return None, f"S3 delete failed: {str(e)}"

        repo_delete(prompt_id)
        return {"message": f"Prompt {prompt_id} deleted successfully"}, None
    except Exception as e:
        return None, str(e)


def generate_upload_url(prompt_id, query_params):
    """Generate presigned URL for file upload."""
    filename = (query_params or {}).get("file_name", f"prompt_{prompt_id}.txt")

    try:
        prompt = get_basic_prompt_by_id(prompt_id)
        if not prompt:
            return None, f"Prompt {prompt_id} not found"

        key = _make_key(prompt["organization_id"], filename)
        upload_url = _presigned_put(key)
        new_url = _s3_url(key)

        update_file_url(prompt_id, new_url)

        return {
            "upload_url": upload_url,
            "file_url": new_url,
            "message": "PUT your file binary to upload_url.",
        }, None
    except Exception as e:
        return None, str(e)


def get_file_content(prompt_id):
    """Get the content of the prompt instruction file from S3 for preview."""
    try:
        prompt = get_basic_prompt_by_id(prompt_id)
        if not prompt:
            return None, f"Prompt {prompt_id} not found"

        file_url = prompt.get("prompt_file_url")
        if not file_url:
            return None, "No file attached to this prompt"

        # Extract key from S3 URL
        key = file_url.split(f"s3://{S3_BUCKET}/")[1]

        # Get file from S3
        response = s3.get_object(Bucket=S3_BUCKET, Key=key)
        content = response["Body"].read().decode("utf-8")

        return {
            "file_name": key,
            "content": content,
        }, None
    except s3.exceptions.NoSuchKey:
        return None, "File not found in S3"
    except Exception as e:
        return None, str(e)
