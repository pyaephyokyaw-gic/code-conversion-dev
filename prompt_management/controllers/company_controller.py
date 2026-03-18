"""
Company Controller
Handles HTTP request/response for company operations
"""
from models.response import success, server_error
from services.company_service import get_companies


def handle_list_companies(query_params):
    """GET /prompts/companies - List companies, optionally filtered by organization_id."""
    org_id = (query_params or {}).get("organization_id")
    data, err = get_companies(org_id)
    if err:
        return server_error(err)
    return success(data)
