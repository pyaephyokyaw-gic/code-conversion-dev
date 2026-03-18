"""
Company Service
Contains business logic for company operations
"""
from repositories.company_repository import (
    find_all_companies,
    find_companies_by_organization
)


def get_companies(org_id=None):
    """Get companies, optionally filtered by organization."""
    try:
        if org_id:
            companies = find_companies_by_organization(int(org_id))
        else:
            companies = find_all_companies()
        return {"companies": companies}, None
    except Exception as e:
        return None, str(e)
