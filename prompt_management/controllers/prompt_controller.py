"""
Prompt Controller
Handles HTTP request/response for prompt operations
All handlers require cognito_sub for role-based access control
"""
from models.response import success, created, error, not_found, server_error, forbidden
from services.prompt_service import (
    create_prompt,
    get_prompt_by_id,
    list_prompts,
    update_prompt,
    delete_prompt,
    generate_upload_url,
    get_file_content,
    get_prompt_types_dropdown
)


def _handle_auth_error(err):
    """Handle authentication/authorization errors."""
    if "not found" in err.lower():
        return forbidden(err)
    if "access denied" in err.lower() or "not authorized" in err.lower():
        return forbidden(err)
    return server_error(err)


def handle_create(cognito_sub, body):
    """POST /prompts - Create a new prompt."""
    data, err = create_prompt(cognito_sub, body)
    if err:
        if "required" in err:
            return error(err)
        if "not found" in err.lower() or "access denied" in err.lower():
            return forbidden(err)
        return server_error(err)
    return created(data)


def handle_list(cognito_sub, query_params):
    """GET /prompts - List prompts based on user role."""
    data, err = list_prompts(cognito_sub, query_params)
    if err:
        return _handle_auth_error(err)
    return success(data)


def handle_get(cognito_sub, prompt_id):
    """GET /prompts/{id} - Get a prompt by ID."""
    data, err = get_prompt_by_id(cognito_sub, int(prompt_id))
    if err:
        if "not found" in err.lower():
            return not_found(err)
        if "access denied" in err.lower():
            return forbidden(err)
        return server_error(err)
    return success(data)


def handle_update(cognito_sub, prompt_id, body):
    """PUT /prompts/{id} - Update a prompt."""
    data, err = update_prompt(cognito_sub, int(prompt_id), body)
    if err:
        if "not found" in err.lower():
            return not_found(err)
        if "access denied" in err.lower():
            return forbidden(err)
        return server_error(err)
    return success(data)


def handle_delete(cognito_sub, prompt_id):
    """DELETE /prompts/{id} - Delete a prompt."""
    data, err = delete_prompt(cognito_sub, int(prompt_id))
    if err:
        if "not found" in err.lower():
            return not_found(err)
        if "access denied" in err.lower():
            return forbidden(err)
        return server_error(err)
    return success(data)


def handle_upload_url(cognito_sub, prompt_id, query_params):
    """GET /prompts/{id}/upload-url - Get presigned upload URL."""
    data, err = generate_upload_url(cognito_sub, int(prompt_id), query_params)
    if err:
        if "not found" in err.lower():
            return not_found(err)
        if "access denied" in err.lower():
            return forbidden(err)
        return server_error(err)
    return success(data)


def handle_file_content(cognito_sub, prompt_id):
    """GET /prompts/{id}/file-content - Get file content for preview."""
    data, err = get_file_content(cognito_sub, int(prompt_id))
    if err:
        if "not found" in err.lower():
            return not_found(err)
        if "access denied" in err.lower():
            return forbidden(err)
        return server_error(err)
    return success(data)


def handle_prompt_types_dropdown(cognito_sub):
    """GET /prompts/types - Get prompt types dropdown based on user's company."""
    data, err = get_prompt_types_dropdown(cognito_sub)
    if err:
        return _handle_auth_error(err)
    return success(data)
