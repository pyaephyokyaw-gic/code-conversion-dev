"""
Lambda Handler for Organization Management
Entry point - routes requests to controllers with Cognito authentication

API Routes:
- POST   /organizations                 - Create organization
- GET    /organizations                 - List organizations (with search & pagination)
- GET    /organizations/{org_id}        - Get organization details
- PUT    /organizations/{org_id}        - Update organization
- DELETE /organizations/{org_id}        - Delete organization
- GET    /organizations/dropdown        - Get organizations for dropdown (simple list)
"""
import json
from controllers.organization_controller import (
    handle_create, handle_list, handle_get, handle_update,
    handle_delete, handle_dropdown
)
from models.response import error, not_found, unauthorized


def get_cognito_sub(event):
    """Extract Cognito sub from request headers or query parameters."""
    headers = event.get('headers') or {}
    query_params = event.get('queryStringParameters') or {}
    
    # Check various header cases (API Gateway may lowercase)
    sub = (
        headers.get('sub') or 
        headers.get('Sub') or 
        headers.get('SUB') or
        query_params.get('sub')
    )
    
    # Debug: print headers to see what's coming through
    print(f"DEBUG - Headers received: {headers}")
    print(f"DEBUG - Sub value: {sub}")
    
    return sub


def lambda_handler(event, context):
    """Main Lambda handler - routes requests to appropriate controllers."""
    method = event.get("httpMethod", "")
    path = event.get("path", "")
    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}

    # Get Cognito sub for authentication
    cognito_sub = get_cognito_sub(event)
    if not cognito_sub:
        return unauthorized("sub token missing")

    body = {}
    if event.get("body"):
        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return error("Invalid JSON body")

    org_id = path_params.get("org_id")

    # ── Dropdown route ────────────────────────────────────────────────────────

    # GET /organizations/dropdown
    if method == "GET" and path.endswith("/dropdown"):
        return handle_dropdown(cognito_sub, query_params)

    # ── Organization CRUD routes ──────────────────────────────────────────────

    # POST /organizations - Create organization
    if method == "POST" and path.endswith("/organizations"):
        return handle_create(cognito_sub, body)

    # GET /organizations - List organizations
    if method == "GET" and path.endswith("/organizations"):
        return handle_list(cognito_sub, query_params)

    # GET /organizations/{org_id}
    if method == "GET" and org_id:
        return handle_get(cognito_sub, org_id)

    # PUT /organizations/{org_id}
    if method == "PUT" and org_id:
        return handle_update(cognito_sub, org_id, body)

    # DELETE /organizations/{org_id}
    if method == "DELETE" and org_id:
        return handle_delete(cognito_sub, org_id)

    return not_found("Route not found")
