from repositories.company_repository import (
    create_company as repo_create_company,
    get_company_by_id as repo_get_by_id,
    list_companies as repo_list,
    search_companies as repo_search,
    get_companies_by_organization as repo_by_org,
    update_company as repo_update,
    delete_company as repo_delete
)


# ─────────────────────────────
# CREATE COMPANY
# ─────────────────────────────
def create_company(body):
    if not body.get("name"):
        return None, "name is required"

    if not body.get("organization_id"):
        return None, "organization_id is required"

    try:
        result = repo_create_company(body)
        return {"company": result}, None
    except Exception as e:
        return None, str(e)


# ─────────────────────────────
# GET BY ID
# ─────────────────────────────
def get_company_by_id(company_id):
    try:
        company = repo_get_by_id(company_id)
        if not company:
            return None, "Company not found"
        return {"company": company}, None
    except Exception as e:
        return None, str(e)


# ─────────────────────────────
# LIST COMPANIES
# ─────────────────────────────
def list_companies(params):
    try:
        page = int(params.get("page", 1))
        limit = int(params.get("limit", 10))
        search = params.get("search")

        result = repo_list(search, page, limit)
        return result, None
    except Exception as e:
        return None, str(e)


# ─────────────────────────────
# SEARCH COMPANIES
# ─────────────────────────────
def search_companies(params):
    name = params.get("name", "")

    try:
        companies = repo_search(name)
        return {"companies": companies}, None
    except Exception as e:
        return None, str(e)


# ─────────────────────────────
# BY ORGANIZATION
# ─────────────────────────────
def get_companies_by_organization(params):
    org_id = params.get("organization_id")

    if not org_id:
        return None, "organization_id required"

    try:
        companies = repo_by_org(int(org_id))
        return {"companies": companies}, None
    except Exception as e:
        return None, str(e)


# ─────────────────────────────
# UPDATE COMPANY
# ─────────────────────────────
def update_company(company_id, body):
    try:
        result = repo_update(company_id, body)
        if not result:
            return None, "Company not found"
        return {"company": result}, None
    except Exception as e:
        return None, str(e)


# ─────────────────────────────
# DELETE COMPANY
# ─────────────────────────────
def delete_company(company_id):
    try:
        success = repo_delete(company_id)
        if not success:
            return None, "Company not found"
        return {"message": "Deleted successfully"}, None
    except Exception as e:
        return None, str(e)