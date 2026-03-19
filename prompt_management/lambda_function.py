"""
Lambda Handler for Prompt Management
Entry point - routes requests to controllers
All APIs require authentication via cognito sub

API Routes:
- POST   /prompts                           - Create prompt
- GET    /prompts                           - List prompts (role-based)
- GET    /prompts/{prompt_id}               - Get prompt details
- PUT    /prompts/{prompt_id}               - Update prompt
- DELETE /prompts/{prompt_id}               - Delete prompt
- GET    /prompts/{prompt_id}/upload-url    - Get presigned upload URL
- GET    /prompts/{prompt_id}/file-content  - Get file content for preview
- GET    /prompts/types                     - Get prompt types dropdown (user's company)
"""
import json
from controllers.prompt_controller import (
    handle_create, handle_list, handle_get, handle_update,
    handle_delete, handle_upload_url, handle_file_content,
    handle_prompt_types_dropdown
)
from models.response import error, not_found


def get_cognito_sub(event):
    """Extract cognito sub (user ID) from request."""
    # For testing: allow sub in headers or query params
    headers = event.get("headers") or {}
    sub = headers.get("sub") or headers.get("Sub")
    if sub:
        return sub
    
    query_params = event.get("queryStringParameters") or {}
    sub = query_params.get("sub")
    if sub:
        return sub
    
    # For Cognito User Pool authorizer
    request_context = event.get("requestContext", {})
    authorizer = request_context.get("authorizer", {})
    claims = authorizer.get("claims", {})
    if claims:
        return claims.get("sub")
    
    # For Lambda authorizer
    if authorizer.get("sub"):
        return authorizer.get("sub")
    
    return None


def lambda_handler(event, context):
    """Main Lambda handler - routes requests to appropriate controllers."""
    method = event.get("httpMethod", "")
    path = event.get("path", "")
    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}

    # Get cognito sub - required for all APIs
    cognito_sub = get_cognito_sub(event)
    if not cognito_sub:
        return error("Authentication required - sub token missing", 401)

    body = {}
    if event.get("body"):
        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return error("Invalid JSON body")

    prompt_id = path_params.get("prompt_id")

    # ── Dropdown routes ───────────────────────────────────────────────────────

    # GET /prompts/types - Prompt types dropdown based on user's company
    if method == "GET" and path.endswith("/types"):
        return handle_prompt_types_dropdown(cognito_sub)

    # ── Prompt sub-resource routes ────────────────────────────────────────────

    # GET /prompts/{prompt_id}/upload-url
    if method == "GET" and prompt_id and path.endswith("/upload-url"):
        return handle_upload_url(cognito_sub, prompt_id, query_params)

    # GET /prompts/{prompt_id}/file-content
    if method == "GET" and prompt_id and path.endswith("/file-content"):
        return handle_file_content(cognito_sub, prompt_id)

    # ── Prompt CRUD routes ────────────────────────────────────────────────────

    # POST /prompts - Create prompt
    if method == "POST" and path.endswith("/prompts"):
        return handle_create(cognito_sub, body)

    # GET /prompts - List prompts (role-based)
    if method == "GET" and path.endswith("/prompts"):
        return handle_list(cognito_sub, query_params)

    # GET /prompts/{prompt_id}
    if method == "GET" and prompt_id:
        return handle_get(cognito_sub, prompt_id)

    # PUT /prompts/{prompt_id}
    if method == "PUT" and prompt_id:
        return handle_update(cognito_sub, prompt_id, body)

    # DELETE /prompts/{prompt_id}
    if method == "DELETE" and prompt_id:
        return handle_delete(cognito_sub, prompt_id)

    return not_found("Route not found")
