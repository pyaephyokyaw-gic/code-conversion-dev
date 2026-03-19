"""
Lambda Handler for Prompt Management
Entry point - routes requests to controllers

API Routes:
- POST   /prompts                           - Create prompt
- GET    /prompts                           - List prompts (grouped by org > company)
- GET    /prompts/{prompt_id}               - Get prompt details
- PUT    /prompts/{prompt_id}               - Update prompt
- DELETE /prompts/{prompt_id}               - Delete prompt
- GET    /prompts/{prompt_id}/upload-url    - Get presigned upload URL
- GET    /prompts/{prompt_id}/file-content  - Get file content for preview
"""
import json
from controllers.prompt_controller import (
    handle_create, handle_list, handle_get, handle_update,
    handle_delete, handle_upload_url, handle_file_content
)
from models.response import error, not_found


def lambda_handler(event, context):
    """Main Lambda handler - routes requests to appropriate controllers."""
    method = event.get("httpMethod", "")
    path = event.get("path", "")
    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}

    body = {}
    if event.get("body"):
        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return error("Invalid JSON body")

    prompt_id = path_params.get("prompt_id")

    # ── Prompt sub-resource routes ────────────────────────────────────────────

    # GET /prompts/{prompt_id}/upload-url
    if method == "GET" and prompt_id and path.endswith("/upload-url"):
        return handle_upload_url(prompt_id, query_params)

    # GET /prompts/{prompt_id}/file-content
    if method == "GET" and prompt_id and path.endswith("/file-content"):
        return handle_file_content(prompt_id)

    # ── Prompt CRUD routes ────────────────────────────────────────────────────

    # POST /prompts - Create prompt
    if method == "POST" and path.endswith("/prompts"):
        return handle_create(body)

    # GET /prompts - List prompts (grouped by org > company)
    if method == "GET" and path.endswith("/prompts"):
        return handle_list(query_params)

    # GET /prompts/{prompt_id}
    if method == "GET" and prompt_id:
        return handle_get(prompt_id)

    # PUT /prompts/{prompt_id}
    if method == "PUT" and prompt_id:
        return handle_update(prompt_id, body)

    # DELETE /prompts/{prompt_id}
    if method == "DELETE" and prompt_id:
        return handle_delete(prompt_id)

    return not_found("Route not found")
