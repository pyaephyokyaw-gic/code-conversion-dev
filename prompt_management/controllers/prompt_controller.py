"""
Prompt Controller
Handles HTTP request/response for prompt operations
No business logic here - only validates request and calls service
"""
from models.response import success, created, error, not_found, server_error
from services.prompt_service import (
    create_prompt,
    get_prompt_by_id,
    list_prompts,
    update_prompt,
    delete_prompt,
    generate_upload_url,
    get_file_content
)


def handle_create(body):
    """POST /prompts - Create a new prompt."""
    data, err = create_prompt(body)
    if err:
        if "required" in err:
            return error(err)
        return server_error(err)
    return created(data)


def handle_list(query_params):
    """GET /prompts - List all prompts with filtering."""
    data, err = list_prompts(query_params)
    if err:
        return server_error(err)
    return success(data)


def handle_get(prompt_id):
    """GET /prompts/{id} - Get a prompt by ID."""
    data, err = get_prompt_by_id(int(prompt_id))
    if err:
        if "not found" in err:
            return not_found(err)
        return server_error(err)
    return success(data)


def handle_update(prompt_id, body):
    """PUT /prompts/{id} - Update a prompt."""
    data, err = update_prompt(int(prompt_id), body)
    if err:
        if "not found" in err:
            return not_found(err)
        return server_error(err)
    return success(data)


def handle_delete(prompt_id):
    """DELETE /prompts/{id} - Delete a prompt."""
    data, err = delete_prompt(int(prompt_id))
    if err:
        if "not found" in err:
            return not_found(err)
        return server_error(err)
    return success(data)


def handle_upload_url(prompt_id, query_params):
    """GET /prompts/{id}/upload-url - Get presigned upload URL."""
    data, err = generate_upload_url(int(prompt_id), query_params)
    if err:
        if "not found" in err:
            return not_found(err)
        return server_error(err)
    return success(data)


def handle_file_content(prompt_id):
    """GET /prompts/{id}/file-content - Get file content for preview."""
    data, err = get_file_content(int(prompt_id))
    if err:
        if "not found" in err:
            return not_found(err)
        return server_error(err)
    return success(data)
