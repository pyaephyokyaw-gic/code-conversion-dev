"""
Organization Service
Contains business logic for organization operations
"""
from repositories.organization_repository import find_all_organizations


def get_all_organizations():
    """Get all organizations for dropdown."""
    try:
        organizations = find_all_organizations()
        return {"organizations": organizations}, None
    except Exception as e:
        return None, str(e)
