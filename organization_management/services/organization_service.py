"""
Organization Service
Contains business logic for organization operations with role-based access control
"""
from repositories.organization_repository import (
    create_organization as repo_create,
    get_organization_by_id as repo_get_by_id,
    get_organization_by_name,
    update_organization as repo_update,
    delete_organization as repo_delete,
    list_organizations as repo_list,
    find_all_organizations,
    find_organizations_by_ids,
    has_companies
)
from repositories.user_repository import get_user_by_cognito_id


def _get_user_or_error(cognito_sub):
    """Get user by cognito_sub or return error."""
    user = get_user_by_cognito_id(cognito_sub)
    if not user:
        return None, "User not found"
    return user, None


def create_organization(cognito_sub, body):
    """Create a new organization - only super_admin allowed."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    # Only super_admin can create organizations
    if user.get("role") != "super_admin":
        return None, "Access denied - only super_admin can create organizations"

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


def get_organization_by_id(cognito_sub, org_id):
    """Get an organization by ID with role-based access."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    role = user.get("role")
    user_org_id = user.get("organization_id")

    # Only super_admin can view any org, others can only view their own
    if role != "super_admin" and org_id != user_org_id:
        return None, "Access denied - you can only view your own organization"

    try:
        org = repo_get_by_id(org_id)
        if not org:
            return None, f"Organization {org_id} not found"
        return {"organization": org}, None
    except Exception as e:
        return None, str(e)


def list_organizations(cognito_sub, query_params):
    """List organizations with role-based filtering."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    role = user.get("role")
    user_org_id = user.get("organization_id")

    qp = query_params or {}
    search = qp.get("search")
    page = max(int(qp.get("page", 1)), 1)
    limit = max(int(qp.get("limit", 10)), 1)

    try:
        if role == "super_admin":
            # Super admin: see all organizations
            result = repo_list(search, page, limit)
        else:
            # Others: only see their own organization
            result = repo_list(search, page, limit, organization_id=user_org_id)

        return result, None
    except Exception as e:
        return None, str(e)


def update_organization(cognito_sub, org_id, body):
    """Update an organization with role-based access."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    role = user.get("role")
    user_org_id = user.get("organization_id")

    # Only super_admin can update any org, org_admin can update their own
    if role == "super_admin":
        pass  # Can update any
    elif role == "org_admin" and org_id == user_org_id:
        pass  # Can update their own
    else:
        return None, "Access denied - insufficient permissions to update this organization"

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


def delete_organization(cognito_sub, org_id):
    """Delete an organization - only super_admin allowed."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    # Only super_admin can delete organizations
    if user.get("role") != "super_admin":
        return None, "Access denied - only super_admin can delete organizations"

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


def get_all_organizations(cognito_sub):
    """Get organizations for dropdown with role-based access."""
    user, err = _get_user_or_error(cognito_sub)
    if err:
        return None, err

    role = user.get("role")
    user_org_id = user.get("organization_id")

    try:
        if role == "super_admin":
            # Super admin: see all organizations
            organizations = find_all_organizations()
        else:
            # Others: only see their own organization
            organizations = find_organizations_by_ids([user_org_id])

        return {"organizations": organizations}, None
    except Exception as e:
        return None, str(e)
