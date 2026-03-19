"""
Organization Controller
Handles HTTP request/response for organization operations
No business logic here - only validates request and calls service
"""
from models.response import success, created, error, not_found, server_error
from services.organization_service import (
    create_organization,
    get_organization_by_id,
    list_organizations,
    update_organization,
    delete_organization,
    get_all_organizations
)


def handle_create(body):
    """POST /organizations - Create a new organization."""
    data, err = create_organization(body)
    if err:
        if "required" in err or "cannot be empty" in err:
            return error(err)
        if "already exists" in err:
            return error(err, 409)
        return server_error(err)
    return created(data)


def handle_list(query_params):
    """GET /organizations - List all organizations with pagination."""
    data, err = list_organizations(query_params)
    if err:
        return server_error(err)
    return success(data)


def handle_get(org_id):
    """GET /organizations/{id} - Get an organization by ID."""
    data, err = get_organization_by_id(int(org_id))
    if err:
        if "not found" in err:
            return not_found(err)
        return server_error(err)
    return success(data)


def handle_update(org_id, body):
    """PUT /organizations/{id} - Update an organization."""
    data, err = update_organization(int(org_id), body)
    if err:
        if "not found" in err:
            return not_found(err)
        if "already exists" in err:
            return error(err, 409)
        if "cannot be empty" in err:
            return error(err)
        return server_error(err)
    return success(data)


def handle_delete(org_id):
    """DELETE /organizations/{id} - Delete an organization."""
    data, err = delete_organization(int(org_id))
    if err:
        if "not found" in err:
            return not_found(err)
        if "Cannot delete" in err:
            return error(err, 409)
        return server_error(err)
    return success(data)


def handle_dropdown(query_params):
    """GET /organizations/dropdown - Get organizations for dropdown."""
    data, err = get_all_organizations()
    if err:
        return server_error(err)
    return success(data)
