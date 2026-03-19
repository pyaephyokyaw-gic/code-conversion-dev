"""
Prompt Service
Contains business logic for prompt operations with role-based access control
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
    list_prompts_grouped,
    list_prompts_by_company,
    get_prompt_types_by_company,
    get_all_prompt_types,
    get_prompt_types_by_organization
)
from repositories.user_repository import get_user_by_cognito_id

S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
AWS_REGION = os.environ.get("AWS_REGION_NAME", "ap-northeast-1")
s3 = boto3.client("s3", region_name=AWS_REGION)


def _get_user_or_error(cognito_sub):
    """Get user by cognito_sub or return error."""
    user = get_user_by_cognito_id(cognito_sub)
    if not user:
        return None, "User not found"
    return user, None


def _check_prompt_access(user, prompt):
    """Check if user has access to the prompt based on role."""
    role = user.get("role")
    
    if role == "super_admin":
        return True
    elif role == "org_admin":
        return prompt.get("organization_id") == user.get("organization_id")
    else:  # member
        return prompt.get("company_id") == user.get("company_id")


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


def create_prompt(cognito_sub, body):
    """Create a new prompt with role-based access control."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    role = user.get("role")
    user_org_id = user.get("organization_id")
    user_company_id = user.get("company_id")

    org_id = body.get("organization_id")
    company_id = body.get("company_id")

    # Role-based validation
    if role == "super_admin":
        # Super admin can create for any org/company
        if not org_id:
            return None, "organization_id is required"
        if not company_id:
            return None, "company_id is required"
    elif role == "org_admin":
        # Org admin can only create for their organization
        org_id = user_org_id
        if not company_id:
            return None, "company_id is required"
    else:  # member
        # Member can only create for their company
        org_id = user_org_id
        company_id = user_company_id

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


def get_prompt_by_id(cognito_sub, prompt_id):
    """Get a prompt by ID with role-based access control."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    try:
        prompt = repo_get_by_id(prompt_id)
        if not prompt:
            return None, f"Prompt {prompt_id} not found"

        # Check access
        if not _check_prompt_access(user, prompt):
            return None, "Access denied - you can only view prompts from your company"

        return {"prompt": prompt}, None
    except Exception as e:
        return None, str(e)


def list_prompts(cognito_sub, query_params):
    """List prompts with role-based filtering."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    role = user.get("role")
    user_org_id = user.get("organization_id")
    user_company_id = user.get("company_id")

    qp = query_params or {}
    search = qp.get("search")
    page = max(int(qp.get("page", 1)), 1)
    limit = max(int(qp.get("limit", 5)), 1)

    try:
        if role == "super_admin":
            # Super admin: can see all or filter by org/company from query
            org_id = qp.get("organization_id")
            company_id = qp.get("company_id")
            result = list_prompts_grouped(org_id, company_id, search, page, limit)
        elif role == "org_admin":
            # Org admin: can only see their organization's prompts
            company_id = qp.get("company_id")  # can filter by company within org
            result = list_prompts_grouped(user_org_id, company_id, search, page, limit)
        else:  # member
            # Member: can only see their company's prompts
            result = list_prompts_by_company(user_company_id, search, page, limit)

        return result, None
    except Exception as e:
        return None, str(e)


def update_prompt(cognito_sub, prompt_id, body):
    """Update a prompt with role-based access control."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    try:
        existing = get_basic_prompt_by_id(prompt_id)
        if not existing:
            return None, f"Prompt {prompt_id} not found"

        # Check access
        if not _check_prompt_access(user, existing):
            return None, "Access denied - you can only update prompts from your company"

        role = user.get("role")
        org_id = body.get("organization_id")
        company_id = body.get("company_id")

        # Non-super_admin cannot change org/company
        if role != "super_admin":
            org_id = None
            company_id = None

        name = body.get("prompt_name")
        description = body.get("prompt_description")
        input_file_type = body.get("input_file_type")
        output_file_type = body.get("output_file_type")
        filename = body.get("file_name")
        content = body.get("prompt_content")

        old_file_url = existing.get("prompt_file_url")
        file_url = None
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


def delete_prompt(cognito_sub, prompt_id):
    """Delete a prompt with role-based access control."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    try:
        existing = get_basic_prompt_by_id(prompt_id)
        if not existing:
            return None, f"Prompt {prompt_id} not found"

        # Check access
        if not _check_prompt_access(user, existing):
            return None, "Access denied - you can only delete prompts from your company"

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


def generate_upload_url(cognito_sub, prompt_id, query_params):
    """Generate presigned URL with role-based access control."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    filename = (query_params or {}).get("file_name", f"prompt_{prompt_id}.txt")

    try:
        prompt = get_basic_prompt_by_id(prompt_id)
        if not prompt:
            return None, f"Prompt {prompt_id} not found"

        # Check access
        if not _check_prompt_access(user, prompt):
            return None, "Access denied - you can only upload to prompts from your company"

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


def get_file_content(cognito_sub, prompt_id):
    """Get file content with role-based access control."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    try:
        prompt = get_basic_prompt_by_id(prompt_id)
        if not prompt:
            return None, f"Prompt {prompt_id} not found"

        # Check access
        if not _check_prompt_access(user, prompt):
            return None, "Access denied - you can only view files from your company's prompts"

        file_url = prompt.get("prompt_file_url")
        if not file_url:
            return None, "No file attached to this prompt"

        key = file_url.split(f"s3://{S3_BUCKET}/")[1]
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


def get_prompt_types_dropdown(cognito_sub):
    """Get prompt types for dropdown based on user's role."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    role = user.get("role")
    organization_id = user.get("organization_id")
    company_id = user.get("company_id")

    try:
        if role == "super_admin":
            prompt_types = get_all_prompt_types()
        elif role == "org_admin":
            prompt_types = get_prompt_types_by_organization(organization_id)
        else:  # member
            prompt_types = get_prompt_types_by_company(company_id)

        return {
            "user": {
                "id": user["id"],
                "name": user["name"],
                "role": role,
                "organization_id": organization_id,
                "company_id": company_id
            },
            "prompt_types": prompt_types
        }, None
    except Exception as e:
        return None, str(e)
