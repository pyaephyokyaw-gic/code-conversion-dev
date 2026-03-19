"""
Organization Service
Contains business logic for organization operations
"""
from repositories.organization_repository import (
    create_organization as repo_create,
    get_organization_by_id as repo_get_by_id,
    get_organization_by_name,
    update_organization as repo_update,
    delete_organization as repo_delete,
    list_organizations as repo_list,
    find_all_organizations,
    has_companies
)


def create_organization(body):
    """Create a new organization."""
    name = body.get("name")
    
    if not name:
        return None, "name is required"
    
    name = name.strip()
    if not name:
        return None, "name cannot be empty"

    try:
        # Check if organization with same name exists
        existing = get_organization_by_name(name)
        if existing:
            return None, f"Organization with name '{name}' already exists"

        org = repo_create(name)
        return {"organization": org}, None
    except Exception as e:
        return None, str(e)


def get_organization_by_id(org_id):
    """Get an organization by ID."""
    try:
        org = repo_get_by_id(org_id)
        if not org:
            return None, f"Organization {org_id} not found"
        return {"organization": org}, None
    except Exception as e:
        return None, str(e)


def list_organizations(query_params):
    """List organizations with search and pagination."""
    qp = query_params or {}
    search = qp.get("search")
    page = max(int(qp.get("page", 1)), 1)
    limit = max(int(qp.get("limit", 10)), 1)

    try:
        result = repo_list(search, page, limit)
        return result, None
    except Exception as e:
        return None, str(e)


def update_organization(org_id, body):
    """Update an organization."""
    name = body.get("name")
    
    if name is not None:
        name = name.strip()
        if not name:
            return None, "name cannot be empty"

    try:
        existing = repo_get_by_id(org_id)
        if not existing:
            return None, f"Organization {org_id} not found"

        # Check for duplicate name
        if name and name != existing["name"]:
            dup = get_organization_by_name(name)
            if dup:
                return None, f"Organization with name '{name}' already exists"

        updated = repo_update(org_id, name)
        return {"organization": updated}, None
    except Exception as e:
        return None, str(e)


def delete_organization(org_id):
    """Delete an organization."""
    try:
        existing = repo_get_by_id(org_id)
        if not existing:
            return None, f"Organization {org_id} not found"

        # Check if organization has companies
        if has_companies(org_id):
            return None, "Cannot delete organization with existing companies"

        repo_delete(org_id)
        return {"message": f"Organization {org_id} deleted successfully"}, None
    except Exception as e:
        return None, str(e)


def get_all_organizations():
    """Get all organizations for dropdown."""
    try:
        organizations = find_all_organizations()
        return {"organizations": organizations}, None
    except Exception as e:
        return None, str(e)
