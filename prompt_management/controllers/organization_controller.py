"""
Organization Controller
Handles HTTP request/response for organization operations
"""
from models.response import success, server_error
from services.organization_service import get_all_organizations


def handle_list_organizations(query_params):
    """GET /prompts/organizations - List all organizations for dropdown."""
    data, err = get_all_organizations()
    if err:
        return server_error(err)
    return success(data)
